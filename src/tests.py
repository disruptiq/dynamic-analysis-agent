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

    # Wait for application to start up
    logger.info("Waiting for application to start...")
    time.sleep(5)

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
    logger.info(f"Starting vulnerability assessment on {base_url}")
    vulnerabilities = test_vulnerabilities(base_url)
    logger.info(f"Vulnerability assessment completed: found {len(vulnerabilities)} potential issues")
    results["vulnerabilities"].extend(vulnerabilities)
    progress.update()

    # Perform Nmap scan
    progress.update(description="Running Nmap scan")
    logger.info("Starting Nmap network scan")
    nmap_results = perform_nmap_scan("localhost", port)
    if nmap_results:
        results["tools"].append({"name": "nmap", "results": nmap_results})
        logger.info("Nmap scan completed")
    else:
        logger.info("Nmap scan skipped or not available")
    progress.update()

    # Perform Nikto scan
    progress.update(description="Running Nikto scan")
    logger.info("Starting Nikto web server scan")
    nikto_results = perform_nikto_scan(base_url)
    if nikto_results:
        results["tools"].append({"name": "nikto", "results": nikto_results})
        logger.info("Nikto scan completed")
    else:
        logger.info("Nikto scan skipped or not available")
    progress.update()

    # Perform ZAP scan
    progress.update(description="Running OWASP ZAP scan")
    logger.info("Starting OWASP ZAP security scan")
    zap_results = perform_zap_scan(base_url, zap_port)
    if zap_results:
        results["tools"].append({"name": "zap", "results": zap_results})
        logger.info("ZAP scan completed")
    else:
        logger.info("ZAP scan skipped or not available")
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
