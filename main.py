#!/usr/bin/env python3
"""
Dynamic Analysis Agent for Cybersecurity Testing

This script serves as the entry point for performing dynamic cybersecurity tests
on applications running in a sandboxed Docker container environment.
"""

import argparse
import sys
import os

# Add the current directory to Python path for importing src modules
sys.path.insert(0, os.path.dirname(__file__))

from src.docker_manager import run_docker_container
from src.tests import perform_basic_tests
from src.exporters import export_results
from src.utils import cleanup
from src.tools import start_zap, stop_zap
from src.config import config, Config
from src.logger import logger, reload_logger


def main():
    parser = argparse.ArgumentParser(
        description="Dynamic Analysis Agent for Cybersecurity Testing"
    )
    parser.add_argument(
        "--image",
        help="Docker image name to analyze (e.g., myapp:latest)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=config.get("docker.default_port", 8080),
        help=f"Port the application runs on (default: {config.get('docker.default_port', 8080)})"
    )

    parser.add_argument(
        "--output-format",
        choices=["json", "html", "pdf", "csv"],
        default=config.get("reporting.default_format", "json"),
        help=f"Output format for results (default: {config.get('reporting.default_format', 'json')})"
    )
    parser.add_argument(
        "--output-file",
        default="output.json",
        help="Output file path (default: output.json)"
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Path to configuration file (default: auto-detect)"
    )
    parser.add_argument(
        "--create-config",
        action="store_true",
        help="Create a default configuration file and exit"
    )
    parser.add_argument(
        "--api",
        action="store_true",
        help="Run the API server instead of performing a scan"
    )
    parser.add_argument(
        "--api-host",
        default="0.0.0.0",
        help="Host for API server (when using --api)"
    )
    parser.add_argument(
        "--api-port",
        type=int,
        default=5000,
        help="Port for API server (when using --api)"
    )

    args = parser.parse_args()

    # Handle configuration file creation
    if args.create_config:
        Config().create_default_config()
        return

    # Handle API server mode
    if args.api:
        from src.api import run_api
        try:
            run_api(host=args.api_host, port=args.api_port, debug=False)
        except KeyboardInterrupt:
            logger.info("API server stopped by user")
        return

    # Validate required arguments
    if not args.image:
        parser.error("--image is required unless --create-config or --api is used")

    # Load custom configuration if specified
    if args.config:
        import src.config
        src.config.config = Config(args.config)
        reload_logger()  # Reload logger with new config

    base_url = f"http://localhost:{args.port}"

    logger.info("Dynamic Analysis Agent Starting...")
    logger.info(f"Target Image: {args.image}")
    logger.info(f"Target URL: {base_url}")
    logger.debug(f"Configuration loaded from: {config.config_file}")
    logger.debug(f"Output format: {args.output_format}, Output file: {args.output_file}")

    # Start ZAP
    zap_process = start_zap()

    # Run the container
    if not run_docker_container(args.image, port=args.port):
        print("Failed to start container. Exiting.")
        stop_zap(zap_process)
        sys.exit(1)

    scan_results = None
    try:
        # Perform tests
        scan_results = perform_basic_tests(base_url, args.port, zap_port=8090)

        # Export results
        export_results(scan_results, args.output_format, args.output_file)

    finally:
        # Always cleanup
        cleanup(zap_process=zap_process)


if __name__ == "__main__":
    main()
