#!/usr/bin/env python3
"""
Dynamic Analysis Agent for Cybersecurity Testing

This script serves as the entry point for performing dynamic cybersecurity tests
on applications running in a sandboxed Docker container environment.
"""

import argparse
import time
import requests
import sys
import os

# Add the current directory to Python path for importing src modules
sys.path.insert(0, os.path.dirname(__file__))

from src.docker_manager import run_docker_container, cleanup_container
from src.vulnerability_scanner import test_vulnerabilities
from src.tool_integrations import (
    start_zap, perform_zap_scan, stop_zap,
    perform_nmap_scan, perform_nikto_scan
)

def perform_basic_tests(base_url, port, zap_port=8090):
    """
    Perform basic dynamic cybersecurity tests.

    Args:
        base_url (str): Base URL of the application to test
        port (int): Port the application is running on
        zap_port (int): ZAP API port
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

    # Perform Nmap scan
    perform_nmap_scan("localhost", port)

    # Perform Nikto scan
    perform_nikto_scan(base_url)

    # Perform ZAP scan
    perform_zap_scan(base_url, zap_port)

def cleanup(container_name="test-app", zap_process=None):
    """
    Clean up the Docker container and ZAP.

    Args:
        container_name (str): Name of the container to remove
        zap_process (subprocess.Popen): ZAP process to stop
    """
    cleanup_container(container_name)
    stop_zap(zap_process)

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

    # Start ZAP
    zap_process = start_zap()

    # Run the container
    if not run_docker_container(args.image, port=args.port):
        print("Failed to start container. Exiting.")
        stop_zap(zap_process)
        sys.exit(1)

    try:
        # Perform tests
        perform_basic_tests(base_url, args.port, zap_port=8090)
    finally:
        # Always cleanup
        cleanup(zap_process=zap_process)

if __name__ == "__main__":
    main()
