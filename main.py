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
import json
import datetime

# Add the current directory to Python path for importing src modules
sys.path.insert(0, os.path.dirname(__file__))

from src.docker_manager import run_docker_container, cleanup_container
from src.vulnerability_scanner import test_vulnerabilities
from src.tools import (
    start_zap, perform_zap_scan, stop_zap,
    perform_nmap_scan, perform_nikto_scan
)
from src.config import config, Config
from src.logger import logger, reload_logger
from src.progress import ScanProgress

def perform_basic_tests(base_url, port, zap_port=8090):
    """
    Perform basic dynamic cybersecurity tests.

    Args:
        base_url (str): Base URL of the application to test
        port (int): Port the application is running on
        zap_port (int): ZAP API port

    Returns:
        dict: Scan results with vulnerabilities and metadata
    """
    results = {
        "target": base_url,
        "timestamp": time.time(),
        "vulnerabilities": [],
        "tools": [],
        "summary": {}
    }

    # Initialize progress tracking
    progress = ScanProgress(total_steps=6, description="Dynamic Analysis Scan")
    progress.start()

    logger.info(f"Starting dynamic analysis on {base_url}")
    progress.update(description="Checking connectivity")

    # Basic connectivity test
    connectivity_ok = False
    try:
        response = requests.get(base_url, timeout=10)
        logger.info(f"Basic connectivity: Status {response.status_code}")
        if response.status_code >= 200 and response.status_code < 300:
            logger.info("SUCCESS: Application is responding")
            connectivity_ok = True
        else:
            logger.warning("✗ Application returned error status")
    except requests.RequestException as e:
        logger.error(f"✗ Failed to connect to application: {e}")

    results["connectivity"] = connectivity_ok
    progress.update()

    if not connectivity_ok:
        progress.finish()
        return results

    # Test for common vulnerabilities
    progress.update(description="Testing vulnerabilities")
    vulnerabilities = test_vulnerabilities(base_url)
    results["vulnerabilities"].extend(vulnerabilities)
    progress.update()

    # Perform Nmap scan
    progress.update(description="Running Nmap scan")
    nmap_results = perform_nmap_scan("localhost", port)
    if nmap_results:
        results["tools"].append({"name": "nmap", "results": nmap_results})
    progress.update()

    # Perform Nikto scan
    progress.update(description="Running Nikto scan")
    nikto_results = perform_nikto_scan(base_url)
    if nikto_results:
        results["tools"].append({"name": "nikto", "results": nikto_results})
    progress.update()

    # Perform ZAP scan
    progress.update(description="Running OWASP ZAP scan")
    zap_results = perform_zap_scan(base_url, zap_port)
    if zap_results:
        results["tools"].append({"name": "zap", "results": zap_results})
    progress.update(description="Generating summary")

    # Generate summary
    vuln_types = {}
    for vuln in vulnerabilities:
        vuln_type = vuln.get("type", "Unknown")
        vuln_types[vuln_type] = vuln_types.get(vuln_type, 0) + 1

    results["summary"] = {
        "total_vulnerabilities": len(vulnerabilities),
        "vulnerability_types": vuln_types,
        "tools_run": len(results["tools"]),
        "scan_duration": time.time() - results["timestamp"]
    }

    progress.finish()
    logger.info(f"Scan completed. Found {len(vulnerabilities)} vulnerabilities across {len(results['tools'])} tools.")
    logger.debug(f"Scan duration: {results['summary']['scan_duration']:.2f} seconds")
    return results

def export_results(results, output_format="json", output_file=None):
    """
    Export scan results to file.

    Args:
        results (dict): Scan results
        output_format (str): Output format (json, html)
        output_file (str): Output file path
    """
    if not results:
        return

    if not output_file:
        timestamp = datetime.datetime.fromtimestamp(results["timestamp"]).strftime("%Y%m%d_%H%M%S")
        output_file = f"scan_results_{timestamp}.{output_format}"

    if output_format == "json":
        export_json(results, output_file)
    elif output_format == "html":
        export_html(results, output_file)
    else:
        print(f"Unsupported output format: {output_format}")

def export_json(results, output_file):
    """
    Export results to JSON file.

    Args:
        results (dict): Scan results
        output_file (str): Output file path
    """
    try:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"Results exported to {output_file}")
    except Exception as e:
        logger.error(f"Error exporting JSON: {e}")

def export_html(results, output_file):
    """
    Export results to HTML file.

    Args:
        results (dict): Scan results
        output_file (str): Output file path
    """
    try:
        html_content = generate_html_report(results)
        with open(output_file, 'w') as f:
            f.write(html_content)
        logger.info(f"HTML report exported to {output_file}")
    except Exception as e:
        logger.error(f"Error exporting HTML: {e}")

def generate_html_report(results):
    """
    Generate HTML report from scan results.

    Args:
        results (dict): Scan results

    Returns:
        str: HTML content
    """
    timestamp = datetime.datetime.fromtimestamp(results["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dynamic Analysis Scan Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
            .summary {{ background: #e8f4f8; padding: 15px; margin: 20px 0; border-radius: 5px; }}
            .vulnerabilities {{ margin: 20px 0; }}
            .vulnerability {{ border: 1px solid #ddd; padding: 10px; margin: 10px 0; border-radius: 5px; }}
            .high {{ border-left: 5px solid #dc3545; }}
            .medium {{ border-left: 5px solid #ffc107; }}
            .low {{ border-left: 5px solid #28a745; }}
            .tools {{ margin: 20px 0; }}
            .tool {{ background: #f8f9fa; padding: 10px; margin: 10px 0; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Dynamic Analysis Security Scan Report</h1>
            <p><strong>Target:</strong> {results['target']}</p>
            <p><strong>Scan Date:</strong> {timestamp}</p>
        </div>

        <div class="summary">
            <h2>Summary</h2>
            <p><strong>Total Vulnerabilities:</strong> {results['summary']['total_vulnerabilities']}</p>
            <p><strong>Tools Run:</strong> {results['summary']['tools_run']}</p>
            <p><strong>Scan Duration:</strong> {results['summary']['scan_duration']:.2f} seconds</p>
            <p><strong>Connectivity:</strong> {'✓ OK' if results.get('connectivity') else '✗ Failed'}</p>
        </div>

        <div class="vulnerabilities">
            <h2>Vulnerabilities Found ({len(results['vulnerabilities'])})</h2>
    """

    for vuln in results['vulnerabilities']:
        severity_class = "low"
        if "SQL" in vuln['type'] or "Command" in vuln['type']:
            severity_class = "high"
        elif "XSS" in vuln['type']:
            severity_class = "medium"

        html += f"""
            <div class="vulnerability {severity_class}">
                <h3>{vuln['type']}</h3>
                <p><strong>Endpoint:</strong> {vuln['endpoint']}</p>
                <p><strong>Method:</strong> {vuln.get('method', 'N/A')}</p>
                <p><strong>Payload:</strong> {vuln.get('payload', 'N/A')}</p>
                <p><strong>Evidence:</strong> {vuln.get('evidence', 'N/A')}</p>
            </div>
        """

    html += """
        </div>

        <div class="tools">
            <h2>Tool Results</h2>
    """

    for tool in results['tools']:
        html += f"""
            <div class="tool">
                <h3>{tool['name'].upper()}</h3>
                <p><strong>Success:</strong> {tool['results'].get('success', 'Unknown')}</p>
                <p><strong>Timestamp:</strong> {datetime.datetime.fromtimestamp(tool['results'].get('timestamp', 0)).strftime('%H:%M:%S')}</p>
                {"<pre>" + tool['results'].get('output', '') + "</pre>" if tool['results'].get('output') else ""}
            </div>
        """

    html += """
        </div>
    </body>
    </html>
    """

    return html

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
        help="Docker image name to analyze (e.g., myapp:latest)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=config.get("docker.default_port", 8080),
        help=f"Port the application runs on (default: {config.get('docker.default_port', 8080)})"
    )
    parser.add_argument(
        "--url",
        default=None,
        help="Base URL of the application (default: http://localhost:{port})"
    )
    parser.add_argument(
        "--output-format",
        choices=["json", "html"],
        default=config.get("reporting.default_format", "json"),
        help=f"Output format for results (default: {config.get('reporting.default_format', 'json')})"
    )
    parser.add_argument(
        "--output-file",
        default=None,
        help="Output file path (default: auto-generated with timestamp)"
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

    base_url = args.url if args.url else f"http://localhost:{args.port}"

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
