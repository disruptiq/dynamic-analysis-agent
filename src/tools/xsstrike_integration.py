"""
XSStrike (XSS detection) integration for the Dynamic Analysis Agent.

XSStrike is a Cross Site Scripting (XSS) vulnerability scanner and payload generator.
It has a powerful fuzzing engine and provides zero false positive results using
its unique and intelligent payload generation capabilities.

This integration performs advanced XSS detection and testing including:
- Context-aware payload generation
- DOM XSS detection
- WAF bypass techniques
- Parameter-based XSS testing
- Blind XSS detection

Scans for:
- Reflected XSS vulnerabilities
- Stored XSS vulnerabilities
- DOM-based XSS vulnerabilities
- Blind XSS vulnerabilities
- XSS through various injection points
"""

import subprocess
import json
import time
import os

def perform_xsstrike_scan(url, method="GET", data=None, cookie=None, user_agent=None, threads=10, timeout=30):
    """
    Perform XSStrike XSS vulnerability scan.

    Args:
        url (str): Target URL
        method (str): HTTP method
        data (str): POST data
        cookie (str): Cookie string
        user_agent (str): User agent
        threads (int): Number of threads
        timeout (int): Scan timeout

    Returns:
        dict: Scan results
    """
    try:
        print(f"\nRunning XSStrike scan on {url}...")

        cmd = [
            'python3', '/opt/XSStrike/xsstrike.py',
            '-u', url,
            '--threads', str(threads),
            '--timeout', str(timeout),
            '--json',
            '--no-color'
        ]

        if method == "POST" and data:
            cmd.extend(['--data', data])

        if cookie:
            cmd.extend(['--cookie', cookie])

        if user_agent:
            cmd.extend(['--user-agent', user_agent])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)

        # XSStrike doesn't have a standard return code, check output
        if result.returncode == 0 or result.returncode == 1:
            # Try to parse JSON output if available
            try:
                # XSStrike might output JSON, look for it
                output_lines = result.stdout.split('\n')
                json_data = None

                for line in output_lines:
                    if line.strip().startswith('{'):
                        json_data = json.loads(line)
                        break

                return {
                    "json_results": json_data,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "success": True,
                    "timestamp": time.time()
                }
            except:
                return {
                    "output": result.stdout,
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
        print("XSStrike not installed. Skipping XSStrike scan.")
        return None
    except subprocess.TimeoutExpired:
        print("XSStrike scan timed out.")
        return {"error": "Timeout", "success": False, "timestamp": time.time()}
    except Exception as e:
        print(f"Error during XSStrike scan: {e}")
        return {"error": str(e), "success": False, "timestamp": time.time()}

def xsstrike_get_payloads(url, parameter):
    """
    Get XSStrike payloads for a specific parameter.

    Args:
        url (str): Target URL
        parameter (str): Parameter to test

    Returns:
        dict: Payload results
    """
    try:
        cmd = [
            'python3', '/opt/XSStrike/xsstrike.py',
            '-u', url,
            '--param', parameter,
            '--fuzzer',
            '--no-color'
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        return {
            "output": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0,
            "timestamp": time.time()
        }

    except Exception as e:
        return {"error": str(e), "success": False, "timestamp": time.time()}
