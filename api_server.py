#!/usr/bin/env python3
"""
API Server for the Dynamic Analysis Agent.
"""

import argparse
import os
import sys

# Add the current directory to Python path for importing src modules
sys.path.insert(0, os.path.dirname(__file__))

from src.api import run_api
from src.logger import logger
from src.config import config

def main():
    parser = argparse.ArgumentParser(
        description="Dynamic Analysis Agent API Server"
    )
    parser.add_argument(
        "--host",
        default=config.get("api.host", "0.0.0.0"),
        help=f"Host to bind the API server (default: {config.get('api.host', '0.0.0.0')})"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=config.get("api.port", 5000),
        help=f"Port for the API server (default: {config.get('api.port', 5000)})"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=config.get("api.debug", False),
        help="Enable debug mode"
    )

    args = parser.parse_args()

    logger.info("Starting Dynamic Analysis Agent API Server")
    logger.info(f"Host: {args.host}, Port: {args.port}, Debug: {args.debug}")

    try:
        run_api(host=args.host, port=args.port, debug=args.debug)
    except KeyboardInterrupt:
        logger.info("API server stopped by user")
    except Exception as e:
        logger.error(f"API server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
