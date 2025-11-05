"""
Progress bar utilities for the Dynamic Analysis Agent.
"""

import colorama
from colorama import Fore, Style
import threading

colorama.init(autoreset=True)

class ScanProgress:
    """Progress tracking for scan operations."""

    def __init__(self, total_steps=100, description="Scanning"):
        self.total_steps = total_steps
        self.current_step = 0
        self.description = description
        self.lock = threading.Lock()

    def start(self):
        """Start the progress bar."""
        print(f"{Fore.CYAN}{self.description} started...{Style.RESET_ALL}")

    def update(self, steps=1, description=None):
        """Update progress bar."""
        with self.lock:
            self.current_step += steps
            if description:
                self.description = description
            percentage = int((self.current_step / self.total_steps) * 100)
            color = Fore.GREEN if percentage >= 100 else Fore.YELLOW
            print(f"{color}{self.description}: {percentage}% complete{Style.RESET_ALL}")

    def set_description(self, description):
        """Set progress bar description."""
        self.description = description

    def finish(self):
        """Complete the progress bar."""
        print(f"{Fore.GREEN}{self.description} completed!{Style.RESET_ALL}")

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
