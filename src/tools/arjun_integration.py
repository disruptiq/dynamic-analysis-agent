"""
Arjun parameter discovery integration for the Dynamic Analysis Agent.

Arjun is a tool for HTTP parameter discovery and bruteforcing. With a massive
default dictionary of 25,980 parameter names, it can find hidden parameters
that other tools miss.

This integration performs parameter discovery and analysis including:
- Hidden parameter detection
- Parameter bruteforcing with large wordlists
- GET/POST parameter enumeration
- JSON parameter discovery
- XML parameter detection

Scans for:
- Hidden GET parameters
- Hidden POST parameters
- JSON API parameters
- XML API parameters
- Undocumented API endpoints
"""

import subprocess
import json
import time

def perform_arjun_scan(url, method="GET", data=None, wordlist=None, threads=10, timeout=30):
    """
    Perform Arjun parameter discovery.

    Args:
        url (str): Target URL
        method (str): HTTP method
        data (str): POST data for POST requests
        wordlist (str): Custom wordlist path
        threads (int): Number of threads
        timeout (int): Request timeout

    Returns:
        dict: Scan results
    """
    try:
        print(f"\nRunning Arjun parameter discovery on {url}...")

        cmd = [
            'arjun',
            '-u', url,
            '-t', str(threads),
            '--timeout', str(timeout),
            '-oJ', '/dev/stdout'  # JSON output to stdout
        ]

        if method == "POST":
            cmd.extend(['-m', 'POST'])
            if data:
                cmd.extend(['-d', data])

        if wordlist:
            cmd.extend(['-w', wordlist])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)

        if result.returncode == 0:
            try:
                output_data = json.loads(result.stdout)
                parameters = output_data.get('params', [])

                return {
                    "parameters_found": parameters,
                    "count": len(parameters),
                    "json_results": output_data,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "success": True,
                    "timestamp": time.time()
                }
            except json.JSONDecodeError:
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
        print("Arjun not installed. Skipping Arjun scan.")
        return None
    except subprocess.TimeoutExpired:
        print("Arjun scan timed out.")
        return {"error": "Timeout", "success": False, "timestamp": time.time()}
    except Exception as e:
        print(f"Error during Arjun scan: {e}")
        return {"error": str(e), "success": False, "timestamp": time.time()}

def arjun_get_parameters(url, include_common=True):
    """
    Get parameters using Arjun with default wordlist.

    Args:
        url (str): Target URL
        include_common (bool): Include common parameters

    Returns:
        dict: Parameter discovery results
    """
    return perform_arjun_scan(url, threads=20)
