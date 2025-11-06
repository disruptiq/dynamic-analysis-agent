"""
Xsser XSS exploitation integration for the Dynamic Analysis Agent.

Xsser is an automatic framework designed to detect, exploit and report XSS
vulnerabilities in web-based applications.

This integration performs cross-site scripting exploitation including:
- Reflected XSS detection and exploitation
- Stored XSS testing
- DOM-based XSS identification
- Advanced payload generation
- Anti-IDS evasion techniques
- Multiple injection point testing

Used for:
- Cross-site scripting vulnerability testing
- XSS payload development and testing
- Client-side attack simulation
- Web application security assessment
"""

import subprocess
import time

def perform_xsser_scan(base_url, vulnerable_param=None, method='GET', data=None):
    """
    Perform Xsser XSS scan.

    Args:
        base_url (str): Target URL
        vulnerable_param (str): Vulnerable parameter
        method (str): HTTP method
        data (str): POST data

    Returns:
        dict: Scan results
    """
    try:
        print(f"\nRunning Xsser on {base_url}...")

        cmd = ['xsser']

        if method.upper() == 'POST' and data:
            cmd.extend(['-u', f"{base_url}?{data}", '--data', data])
        else:
            cmd.extend(['-u', base_url])

        if vulnerable_param:
            cmd.extend(['-p', vulnerable_param])

        # Add options for comprehensive testing
        cmd.extend(['--auto', '--Coo', '--Xsa', '--Xsr', '--Ind', '--Coo'])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )

        if result.returncode == 0:
            print("Xsser scan completed.")

            # Parse output for XSS findings
            lines = result.stdout.split('\n')
            xss_findings = []
            successful_payloads = []

            for line in lines:
                if '[+] XSS' in line or 'vulnerable' in line.lower():
                    xss_findings.append(line.strip())
                if 'Payload:' in line or 'working' in line.lower():
                    successful_payloads.append(line.strip())

            return {
                "output": result.stdout,
                "base_url": base_url,
                "vulnerable_param": vulnerable_param,
                "method": method,
                "xss_findings": xss_findings,
                "successful_payloads": successful_payloads,
                "vulnerable": len(xss_findings) > 0,
                "success": True,
                "timestamp": time.time()
            }
        else:
            return {
                "error": result.stderr,
                "base_url": base_url,
                "vulnerable_param": vulnerable_param,
                "vulnerable": False,
                "success": False,
                "timestamp": time.time()
            }

    except FileNotFoundError:
        print("Xsser not installed. Skipping XSS testing.")
        return None
    except subprocess.TimeoutExpired:
        print("Xsser timed out.")
        return {
            "error": "Timeout",
            "base_url": base_url,
            "success": False,
            "timestamp": time.time()
        }
    except Exception as e:
        print(f"Error during Xsser scan: {e}")
        return {
            "error": str(e),
            "base_url": base_url,
            "success": False,
            "timestamp": time.time()
        }

def perform_xsser_payload_test(base_url, vulnerable_param, payload):
    """
    Test specific XSS payload.

    Args:
        base_url (str): Target URL
        vulnerable_param (str): Vulnerable parameter
        payload (str): XSS payload to test

    Returns:
        dict: Payload test results
    """
    try:
        print(f"\nTesting XSS payload: {payload}")

        cmd = ['xsser', '-u', base_url, '-p', vulnerable_param, '--payload', payload, '--auto']

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        return {
            "output": result.stdout,
            "error": result.stderr,
            "base_url": base_url,
            "vulnerable_param": vulnerable_param,
            "payload": payload,
            "payload_success": result.returncode == 0 and ('vulnerable' in result.stdout.lower() or '[+]' in result.stdout),
            "success": result.returncode == 0,
            "timestamp": time.time()
        }

    except Exception as e:
        return {
            "error": str(e),
            "base_url": base_url,
            "payload": payload,
            "success": False,
            "timestamp": time.time()
        }
