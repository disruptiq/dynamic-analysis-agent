#!/usr/bin/env python3
"""
Dynamic Analysis Agent for Cybersecurity Testing

This script serves as the entry point for performing dynamic cybersecurity tests
on applications running in a sandboxed Docker container environment.
"""

import argparse
import subprocess
import time
import requests
import sys
from urllib.parse import urljoin

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
        # Wait a bit for the app to start
        time.sleep(5)
        return True

    except FileNotFoundError:
        print("Docker is not installed or not in PATH.")
        return False
    except Exception as e:
        print(f"Error running container: {e}")
        return False

def perform_basic_tests(base_url):
    """
    Perform basic dynamic cybersecurity tests.

    Args:
        base_url (str): Base URL of the application to test
    """
    print(f"Starting dynamic analysis on {base_url}")

    # Basic connectivity test
    try:
        response = requests.get(base_url, timeout=10)
        print(f"Basic connectivity: Status {response.status_code}")
        if response.status_code >= 200 and response.status_code < 300:
            print("✓ Application is responding")
        else:
            print("✗ Application returned error status")
    except requests.RequestException as e:
        print(f"✗ Failed to connect to application: {e}")
        return

    # Test for common vulnerabilities
    test_vulnerabilities(base_url)

def test_vulnerabilities(base_url):
    """
    Test for common web vulnerabilities.

    Args:
        base_url (str): Base URL to test
    """
    print("\nTesting for common vulnerabilities...")

    # Test for SQL Injection (basic)
    sql_payloads = ["' OR '1'='1", "' OR 1=1 --", "admin' --"]
    test_endpoint = urljoin(base_url, "/login")  # Assume a login endpoint

    for payload in sql_payloads:
        try:
            data = {"username": payload, "password": "test"}
            response = requests.post(test_endpoint, data=data, timeout=5)
            if "error" not in response.text.lower() and response.status_code == 200:
                print(f"⚠ Possible SQL injection vulnerability detected with payload: {payload}")
        except:
            pass

    # Test for XSS (basic)
    xss_payloads = ["<script>alert('xss')</script>", "<img src=x onerror=alert('xss')>"]
    test_endpoint = urljoin(base_url, "/search")  # Assume a search endpoint

    for payload in xss_payloads:
        try:
            params = {"q": payload}
            response = requests.get(test_endpoint, params=params, timeout=5)
            if payload in response.text:
                print(f"⚠ Possible XSS vulnerability detected with payload: {payload}")
        except:
            pass

    # Test for directory traversal
    traversal_payloads = ["../../../etc/passwd", "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts"]
    test_endpoint = urljoin(base_url, "/file")  # Assume a file serving endpoint

    for payload in traversal_payloads:
        try:
            params = {"path": payload}
            response = requests.get(test_endpoint, params=params, timeout=5)
            if "root:" in response.text or "hosts" in response.text:
                print(f"⚠ Possible directory traversal vulnerability detected with payload: {payload}")
        except:
            pass

    print("Vulnerability testing completed.")

def cleanup(container_name="test-app"):
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
        print(f"Error during cleanup: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Dynamic Analysis Agent for Cybersecurity Testing"
    )
    parser.add_argument(
        "--image",
        required=True,
        help="Docker image name to analyze (e.g., myapp:latest)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port the application runs on (default: 8080)"
    )
    parser.add_argument(
        "--url",
        default=None,
        help="Base URL of the application (default: http://localhost:{port})"
    )

    args = parser.parse_args()

    base_url = args.url if args.url else f"http://localhost:{args.port}"

    print("Dynamic Analysis Agent Starting...")
    print(f"Target Image: {args.image}")
    print(f"Target URL: {base_url}")

    # Run the container
    if not run_docker_container(args.image, port=args.port):
        print("Failed to start container. Exiting.")
        sys.exit(1)

    try:
        # Perform tests
        perform_basic_tests(base_url)
    finally:
        # Always cleanup
        cleanup()

if __name__ == "__main__":
    main()
