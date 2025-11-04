"""
Progress bar utilities for the Dynamic Analysis Agent.
"""

from tqdm import tqdm
import time
import threading

class ScanProgress:
    """Progress tracking for scan operations."""

    def __init__(self, total_steps=100, description="Scanning"):
        self.total_steps = total_steps
        self.current_step = 0
        self.description = description
        self.pbar = None
        self.lock = threading.Lock()

    def start(self):
        """Start the progress bar."""
        self.pbar = tqdm(total=self.total_steps, desc=self.description, unit="step")

    def update(self, steps=1, description=None):
        """Update progress bar."""
        with self.lock:
            self.current_step += steps
            if description:
                self.pbar.set_description(description)
            self.pbar.update(steps)

    def set_description(self, description):
        """Set progress bar description."""
        if self.pbar:
            self.pbar.set_description(description)

    def finish(self):
        """Complete the progress bar."""
        if self.pbar:
            self.pbar.close()

def with_progress(description="Processing"):
    """Decorator to add progress tracking to functions."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            progress = ScanProgress(description=description)
            progress.start()
            try:
                result = func(progress, *args, **kwargs)
                progress.finish()
                return result
            except Exception as e:
                progress.finish()
                raise e
        return wrapper
    return decorator
