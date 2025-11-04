"""
Jaeles API testing integration for the Dynamic Analysis Agent.

Jaeles is a powerful, flexible and fast framework for testing and discovering
API vulnerabilities. It provides a comprehensive set of tests for REST, GraphQL,
and other API formats.

This integration performs comprehensive API security testing including:
- REST API vulnerability scanning
- GraphQL API testing
- Authentication bypass detection
- Authorization testing
- API fuzzing and parameter testing

Scans for:
- Broken authentication in APIs
- Broken authorization controls
- Mass assignment vulnerabilities
- API injection flaws
- Rate limiting bypasses
"""

import subprocess
import json
import time
import os

def perform_jaeles_scan(url, signatures=None, threads=10, timeout=30):
    """
    Perform Jaeles API security testing.

    Args:
        url (str): Target URL
        signatures (str): Path to signatures directory
        threads (int): Number of threads
        timeout (int): Scan timeout

    Returns:
        dict: Scan results
    """
    try:
        print(f"\nRunning Jaeles scan on {url}...")

        cmd = [
            'jaeles',
            'scan',
            '-u', url,
            '-c', str(threads),
            '--timeout', str(timeout),
            '-o', '/tmp/jaeles_output',
            '--json'
        ]

        if signatures:
            cmd.extend(['-s', signatures])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)

        # Try to read output file
        output_file = '/tmp/jaeles_output/jaeles-output.json'
        findings = []

        if os.path.exists(output_file):
            try:
                with open(output_file, 'r') as f:
                    data = json.load(f)
                    findings = data.get('findings', [])
            except:
                pass

        return {
            "findings": findings,
            "count": len(findings),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0,
            "return_code": result.returncode,
            "timestamp": time.time()
        }

    except FileNotFoundError:
        print("Jaeles not installed. Skipping Jaeles scan.")
        return None
    except subprocess.TimeoutExpired:
        print("Jaeles scan timed out.")
        return {"error": "Timeout", "success": False, "timestamp": time.time()}
    except Exception as e:
        print(f"Error during Jaeles scan: {e}")
        return {"error": str(e), "success": False, "timestamp": time.time()}
