"""
Docker container management for the Dynamic Analysis Agent.
"""

import subprocess

def run_docker_container(image_name, container_name="test-app", port=8080):
    """
    Run the Docker container with the specified image.

    Args:
        image_name (str): Name of the Docker image to run
        container_name (str): Name for the container (default: test-app)
        port (int): Port to expose (default: 8080)

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Stop and remove any existing container with the same name
        subprocess.run(['docker', 'stop', container_name], capture_output=True)
        subprocess.run(['docker', 'rm', container_name], capture_output=True)

        # Run the new container
        cmd = [
            'docker', 'run', '-d',
            '--name', container_name,
            '-p', f'{port}:{port}',
            image_name
        ]
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
