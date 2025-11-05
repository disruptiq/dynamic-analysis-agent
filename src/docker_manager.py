"""
Docker container management for the Dynamic Analysis Agent.
"""

import subprocess

def run_docker_container(image_name, container_name="test-app", ports=None, port=None):
    """
    Run the Docker container with the specified image.

    Args:
    image_name (str): Name of the Docker image to run
    container_name (str): Name for the container (default: test-app)
    ports (list): List of ports to expose (preferred)
        port (int): Single port to expose (deprecated, use ports)

    Returns:
        bool: True if successful, False otherwise
    """
    # Handle backward compatibility
    if ports is None and port is not None:
        ports = [port]
    elif ports is None:
        ports = [8080]  # default
    try:
        # Stop and remove any existing container with the same name
        subprocess.run(['docker', 'stop', container_name], capture_output=True)
        subprocess.run(['docker', 'rm', container_name], capture_output=True)

        # Run the new container with all specified ports
        cmd = ['docker', 'run', '-d', '--name', container_name]
        for p in ports:
            cmd.extend(['-p', f'{p}:{p}'])
        cmd.append(image_name)
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Error running container: {result.stderr}")
            return False

        print(f"Container '{container_name}' started successfully.")
        return True

    except FileNotFoundError:
        print("Docker is not installed or not in PATH.")
        return False
    except Exception as e:
        print(f"Error running container: {e}")
        return False

def cleanup_container(container_name="test-app"):
    """
    Clean up the Docker container.

    Args:
        container_name (str): Name of the container to remove
    """
    try:
        subprocess.run(['docker', 'stop', container_name], capture_output=True)
        subprocess.run(['docker', 'rm', container_name], capture_output=True)
        print(f"Container '{container_name}' cleaned up.")
    except Exception as e:
        print(f"Error during container cleanup: {e}")
