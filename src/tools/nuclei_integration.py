"""
Nuclei template-based scanning integration for the Dynamic Analysis Agent.

Nuclei is a fast, customizable vulnerability scanner based on simple YAML-based
templates. It can detect vulnerabilities in web applications, networks, and cloud
environments with minimal false positives.

This integration performs template-based security scanning including:
- Fast vulnerability detection using community templates
- Custom template execution
- CVE detection and exploitation
- Technology stack identification
- Exposed panel and default credential detection

Scans for:
- Known CVEs and vulnerabilities
- Misconfigured services and applications
- Exposed administrative panels
- Default credentials and weak configurations
- Technology-specific vulnerabilities
"""

import subprocess
import json
import time
import os

def perform_nuclei_scan(target, templates=None, severity="info,low,medium,high,critical", output_format="json", threads=25):
    """
    Perform Nuclei template-based vulnerability scanning.

    Args:
        target (str): Target URL, IP, or file with targets
        templates (str): Template or template directory path
        severity (str): Severity levels to include (comma-separated)
        output_format (str): Output format (json, sarif)
        threads (int): Number of threads

    Returns:
        dict: Scan results
    """
    try:
        print(f"\nRunning Nuclei scan on {target}...")

        cmd = [
            'nuclei',
            '-target', target,
            '-severity', severity,
            '-json',
            '-o', '/dev/stdout',
            '-silent',
            '-no-interactsh',
            '-threads', str(threads)
        ]

        if templates:
            cmd.extend(['-t', templates])

        # Add rate limiting to avoid being too aggressive
        cmd.extend(['-rate-limit', '150'])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)  # 30 min timeout

        if result.returncode == 0:
            # Parse JSON lines output
            lines = result.stdout.strip().split('\n')
            findings = []

            for line in lines:
                if line.strip():
                    try:
                        finding = json.loads(line)
                        findings.append(finding)
                    except json.JSONDecodeError:
                        continue

            return {
                "findings": findings,
                "count": len(findings),
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": True,
                "timestamp": time.time()
            }
        else:
            return {
                "error": result.stderr,
                "stdout": result.stdout,
                "success": False,
                "return_code": result.returncode,
                "timestamp": time.time()
            }

    except FileNotFoundError:
        print("Nuclei not installed. Skipping Nuclei scan.")
        return None
    except subprocess.TimeoutExpired:
        print("Nuclei scan timed out.")
        return {"error": "Timeout", "success": False, "timestamp": time.time()}
    except Exception as e:
        print(f"Error during Nuclei scan: {e}")
        return {"error": str(e), "success": False, "timestamp": time.time()}

def nuclei_cve_scan(target, templates="~/nuclei-templates/cves/"):
    """
    Scan for CVEs using Nuclei.

    Args:
        target (str): Target to scan
        templates (str): CVE templates path

    Returns:
        dict: CVE scan results
    """
    return perform_nuclei_scan(target, templates=templates, severity="high,critical")

def nuclei_technology_scan(target, templates="~/nuclei-templates/technologies/"):
    """
    Technology detection using Nuclei.

    Args:
        target (str): Target to scan
        templates (str): Technology templates path

    Returns:
        dict: Technology scan results
    """
    return perform_nuclei_scan(target, templates=templates, severity="info,low,medium,high,critical")

def nuclei_exposed_panels_scan(target, templates="~/nuclei-templates/exposed-panels/"):
    """
    Exposed panels detection using Nuclei.

    Args:
        target (str): Target to scan
        templates (str): Exposed panels templates path

    Returns:
        dict: Exposed panels scan results
    """
    return perform_nuclei_scan(target, templates=templates, severity="medium,high,critical")

def nuclei_dns_scan(target, templates="~/nuclei-templates/dns/"):
    """
    DNS security checks using Nuclei.

    Args:
        target (str): Target domain
        templates (str): DNS templates path

    Returns:
        dict: DNS scan results
    """
    return perform_nuclei_scan(target, templates=templates, severity="medium,high,critical")
