"""
Nmap integration for the Dynamic Analysis Agent.
"""

import subprocess
import time

def perform_nmap_scan(host, port):
    """
    Perform Nmap port scan.

    Args:
        host (str): Target host
        port (int): Target port

    Returns:
        dict: Scan results or None if failed
    """
    try:
        print(f"\nRunning Nmap scan on {host}:{port}...")
        result = subprocess.run(
            ['nmap', '-sV', '-p', str(port), host],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print("Nmap scan completed.")
            return {
                "output": result.stdout,
                "success": True,
                "timestamp": time.time()
            }
        else:
            print(f"Nmap scan failed: {result.stderr}")
            return {
                "error": result.stderr,
                "success": False,
                "timestamp": time.time()
            }
    except FileNotFoundError:
        print("Nmap not installed. Skipping port scan.")
        return None
    except subprocess.TimeoutExpired:
        print("Nmap scan timed out.")
        return {
            "error": "Timeout",
            "success": False,
            "timestamp": time.time()
        }
    except Exception as e:
        print(f"Error during Nmap scan: {e}")
        return {
            "error": str(e),
            "success": False,
            "timestamp": time.time()
        }
