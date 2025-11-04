"""
Nikto web server scanner integration for the Dynamic Analysis Agent.

Nikto is an open-source web server scanner that performs comprehensive tests
against web servers for multiple items, including over 6700 potentially dangerous
files/programs, checks for outdated versions of over 1250 servers, and version
specific problems on over 270 servers.

This integration performs web server vulnerability scanning including:
- Outdated software version detection
- Potentially dangerous files and directories
- Server configuration issues
- Common web server vulnerabilities
- Default or backup file detection

Scans for:
- Outdated web server software
- Misconfigured servers and applications
- Potentially dangerous CGI scripts
- Default installation files
- Known vulnerable server configurations
"""

import subprocess
import time

def perform_nikto_scan(base_url):
    """
    Perform Nikto web server scan.

    Args:
        base_url (str): Target URL

    Returns:
        dict: Scan results or None if failed
    """
    try:
        print(f"\nRunning Nikto scan on {base_url}...")
        result = subprocess.run(
            ['nikto', '-h', base_url, '-Format', 'txt'],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            print("Nikto scan completed.")
            # Filter out some noise, extract key findings
            lines = result.stdout.split('\n')
            findings = [line for line in lines if '+ ' in line and 'OSVDB' in line]
            return {
                "output": result.stdout,
                "findings": findings,
                "success": True,
                "timestamp": time.time()
            }
        else:
            print(f"Nikto scan failed: {result.stderr}")
            return {
                "error": result.stderr,
                "success": False,
                "timestamp": time.time()
            }
    except FileNotFoundError:
        print("Nikto not installed. Skipping web server scan.")
        return None
    except subprocess.TimeoutExpired:
        print("Nikto scan timed out.")
        return {
            "error": "Timeout",
            "success": False,
            "timestamp": time.time()
        }
    except Exception as e:
        print(f"Error during Nikto scan: {e}")
        return {
            "error": str(e),
            "success": False,
            "timestamp": time.time()
        }
