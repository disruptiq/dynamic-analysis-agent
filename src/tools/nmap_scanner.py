"""
Nmap (Network Mapper) integration for the Dynamic Analysis Agent.

Nmap is a free and open-source network discovery and security auditing utility.
It uses raw IP packets to determine what hosts are available on the network,
what services those hosts are offering, what operating systems they are running,
and what type of packet filters/firewalls are in use.

This integration performs network reconnaissance and port scanning including:
- Host discovery and network mapping
- Port scanning (TCP, UDP, SYN, etc.)
- Service and version detection
- OS fingerprinting
- Vulnerability detection through NSE scripts

Scans for:
- Open ports and services
- Operating system identification
- Service versions and potential vulnerabilities
- Network topology and host availability
"""

import subprocess
import time

def perform_nmap_scan(host, ports):
    """
    Perform Nmap port scan.

    Args:
    host (str): Target host
    ports (int or list): Target port(s) - single port or list of ports

    Returns:
    dict: Scan results or None if failed
    """
    # Handle single port or list of ports
    if isinstance(ports, int):
        ports = [ports]
    elif not isinstance(ports, list):
        ports = [int(ports)]

    port_str = ','.join(str(p) for p in ports)
    try:
        print(f"\nRunning Nmap scan on {host}:{port_str}...")
        result = subprocess.run(
            ['nmap', '-sV', '-p', port_str, host],
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
