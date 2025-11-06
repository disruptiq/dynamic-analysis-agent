"""
DNSRecon DNS enumeration integration for the Dynamic Analysis Agent.

DNSRecon is a powerful DNS enumeration script that can discover DNS records,
perform zone transfers, and enumerate subdomains.

This integration performs comprehensive DNS enumeration including:
- Standard DNS record enumeration (A, AAAA, CNAME, MX, NS, SOA, TXT)
- SRV record discovery
- Zone transfer attempts
- Reverse DNS lookups
- Subdomain brute-forcing
- Google dorking for subdomain discovery

Used for:
- Network reconnaissance and mapping
- Attack surface discovery
- Identifying misconfigured DNS servers
- Finding hidden subdomains and services
"""

import subprocess
import time
import json

def perform_dnsrecon_scan(domain, nameserver=None, wordlist=None):
    """
    Perform DNSRecon DNS enumeration scan.

    Args:
        domain (str): Target domain to enumerate
        nameserver (str): Custom nameserver to use
        wordlist (str): Path to subdomain wordlist for brute-forcing

    Returns:
        dict: Scan results or None if failed
    """
    try:
        print(f"\nRunning DNSRecon on {domain}...")

        # Build command
        cmd = ['dnsrecon', '-d', domain, '-t', 'std', '--json']

        if nameserver:
            cmd.extend(['-n', nameserver])

        if wordlist:
            cmd.extend(['-D', wordlist, '-t', 'brt'])

        print(f"Running command: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout for comprehensive scans
        )

        if result.returncode == 0:
            print("DNSRecon scan completed.")
            # Parse JSON output
            try:
                scan_data = json.loads(result.stdout)
                records = scan_data if isinstance(scan_data, list) else []
                return {
                    "output": scan_data,
                    "records": records,
                    "domain": domain,
                    "record_count": len(records),
                    "success": True,
                    "timestamp": time.time()
                }
            except json.JSONDecodeError:
                # Fallback to text output
                return {
                    "output": result.stdout,
                    "raw_output": result.stdout,
                    "domain": domain,
                    "success": True,
                    "timestamp": time.time()
                }
        else:
            print(f"DNSRecon failed: {result.stderr}")
            return {
                "error": result.stderr,
                "domain": domain,
                "success": False,
                "timestamp": time.time()
            }

    except FileNotFoundError:
        print("DNSRecon not installed. Skipping DNS enumeration.")
        return None
    except subprocess.TimeoutExpired:
        print("DNSRecon timed out.")
        return {
            "error": "Timeout",
            "domain": domain,
            "success": False,
            "timestamp": time.time()
        }
    except Exception as e:
        print(f"Error during DNSRecon scan: {e}")
        return {
            "error": str(e),
            "domain": domain,
            "success": False,
            "timestamp": time.time()
        }

def perform_dnsrecon_zone_transfer(domain, nameserver=None):
    """
    Perform DNS zone transfer attempt.

    Args:
        domain (str): Target domain
        nameserver (str): Specific nameserver to try

    Returns:
        dict: Zone transfer results
    """
    try:
        print(f"\nAttempting zone transfer on {domain}...")

        cmd = ['dnsrecon', '-d', domain, '-t', 'axfr', '--json']

        if nameserver:
            cmd.extend(['-n', nameserver])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode == 0:
            try:
                scan_data = json.loads(result.stdout)
                return {
                    "output": scan_data,
                    "zone_transfer_success": len(scan_data) > 0,
                    "domain": domain,
                    "success": True,
                    "timestamp": time.time()
                }
            except json.JSONDecodeError:
                return {
                    "output": result.stdout,
                    "domain": domain,
                    "success": True,
                    "timestamp": time.time()
                }
        else:
            return {
                "error": result.stderr,
                "domain": domain,
                "zone_transfer_success": False,
                "success": False,
                "timestamp": time.time()
            }

    except Exception as e:
        print(f"Error during zone transfer attempt: {e}")
        return {
            "error": str(e),
            "domain": domain,
            "success": False,
            "timestamp": time.time()
        }
