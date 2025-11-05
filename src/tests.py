"""
Test execution functions for the Dynamic Analysis Agent.
"""

import time
import requests

from .vulnerability_scanner_main import test_vulnerabilities
from .tools import (
    start_zap, perform_zap_scan, stop_zap,
    perform_nmap_scan, perform_nikto_scan
)
from .logger import logger
from .progress import ScanProgress


def perform_basic_tests(ports, zap_port=8090):
    """
    Perform basic dynamic cybersecurity tests on multiple ports.

    Args:
    ports (list): List of ports the application is running on
    zap_port (int): ZAP API port

    Returns:
        dict: Scan results with vulnerabilities and metadata
    """
    results = {
        "targets": [f"http://localhost:{port}" for port in ports],
    "timestamp": time.time(),
    "vulnerabilities": [],
    "tools": [],
    "summary": {}
    }

    # Initialize progress tracking
    progress = ScanProgress(total_steps=6, description="Dynamic Analysis Scan")
    progress.start()

    logger.info(f"Starting dynamic analysis on ports: {ports}")
    progress.update(description="Checking connectivity")

    # Wait for application to start up
    logger.info("Waiting for application to start...")
    time.sleep(5)

    # Basic connectivity test for each port
    connectivity_results = {}
    for port in ports:
        base_url = f"http://localhost:{port}"
        connectivity_ok = False
        try:
            response = requests.get(base_url, timeout=10)
            logger.info(f"Port {port} - Basic connectivity: Status {response.status_code}")
            if response.status_code >= 200 and response.status_code < 300:
                logger.info(f"SUCCESS: Application on port {port} is responding")
                connectivity_ok = True
            else:
                logger.warning(f"✗ Port {port} returned error status")
        except requests.RequestException as e:
            logger.error(f"✗ Failed to connect to port {port}: {e}")
        connectivity_results[port] = connectivity_ok

    results["connectivity"] = connectivity_results
    # Continue if at least one port is accessible
    any_connectivity = any(connectivity_results.values())
    progress.update()

    if not any_connectivity:
        progress.finish()
        return results

    # Test for common vulnerabilities on all accessible ports
    progress.update(description="Testing vulnerabilities")
    all_vulnerabilities = []
    for port in ports:
        if connectivity_results.get(port, False):
            base_url = f"http://localhost:{port}"
            logger.info(f"Starting vulnerability assessment on {base_url}")
            vulnerabilities = test_vulnerabilities(base_url)
            # Add port information to vulnerabilities
            for vuln in vulnerabilities:
                vuln['port'] = port
            all_vulnerabilities.extend(vulnerabilities)
            logger.info(f"Vulnerability assessment on port {port} completed: found {len(vulnerabilities)} potential issues")

    results["vulnerabilities"].extend(all_vulnerabilities)
    progress.update()

    # Perform Nmap scan on all ports
    progress.update(description="Running Nmap scan")
    logger.info("Starting Nmap network scan")
    nmap_results = perform_nmap_scan("localhost", ports)
    if nmap_results:
        results["tools"].append({"name": "nmap", "results": nmap_results})
        logger.info("Nmap scan completed")
    else:
        logger.info("Nmap scan skipped or not available")
    progress.update()

    # Perform Nikto scan on all accessible ports
    progress.update(description="Running Nikto scan")
    logger.info("Starting Nikto web server scan")
    all_nikto_results = []
    for port in ports:
        if connectivity_results.get(port, False):
            base_url = f"http://localhost:{port}"
            nikto_results = perform_nikto_scan(base_url)
            if nikto_results:
                nikto_results['port'] = port  # Add port info
                all_nikto_results.append(nikto_results)
                logger.info(f"Nikto scan on port {port} completed")
            else:
                logger.info(f"Nikto scan on port {port} skipped or not available")

    if all_nikto_results:
        results["tools"].append({"name": "nikto", "results": all_nikto_results})
    progress.update()

    # Perform ZAP scan on all accessible ports
    progress.update(description="Running OWASP ZAP scan")
    logger.info("Starting OWASP ZAP security scan")
    all_zap_results = []
    for port in ports:
        if connectivity_results.get(port, False):
            base_url = f"http://localhost:{port}"
            zap_results = perform_zap_scan(base_url, zap_port)
            if zap_results:
                zap_results['port'] = port  # Add port info
                all_zap_results.append(zap_results)
                logger.info(f"ZAP scan on port {port} completed")
            else:
                logger.info(f"ZAP scan on port {port} skipped or not available")

    if all_zap_results:
        results["tools"].append({"name": "zap", "results": all_zap_results})
    progress.update(description="Generating summary")

    # Generate summary
    vuln_types = {}
    for vuln in results["vulnerabilities"]:
        vuln_type = vuln.get("type", "Unknown")
        vuln_types[vuln_type] = vuln_types.get(vuln_type, 0) + 1

    results["summary"] = {
    "total_vulnerabilities": len(results["vulnerabilities"]),
    "vulnerability_types": vuln_types,
    "tools_run": len(results["tools"]),
    "ports_scanned": len(ports),
        "scan_duration": time.time() - results["timestamp"]
    }

    progress.finish()
    logger.info(f"Scan completed. Found {len(results['vulnerabilities'])} vulnerabilities across {len(results['tools'])} tools on {len(ports)} ports.")
    logger.debug(f"Scan duration: {results['summary']['scan_duration']:.2f} seconds")
    return results
