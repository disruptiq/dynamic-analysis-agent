"""
Utility functions for the Dynamic Analysis Agent.
"""

from .docker_manager import cleanup_container
from .tools import stop_zap


def cleanup(container_name="test-app", zap_process=None):
    """
    Clean up the Docker container and ZAP.

    Args:
        container_name (str): Name of the container to remove
        zap_process (subprocess.Popen): ZAP process to stop
    """
    cleanup_container(container_name)
    stop_zap(zap_process)
