"""
Nikto integration for the Dynamic Analysis Agent.
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
