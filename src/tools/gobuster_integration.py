"""
Gobuster (directory/file enumeration) integration for the Dynamic Analysis Agent.

Gobuster is a tool used to brute-force URIs (directories and files) in web sites,
DNS subdomains, and virtual host names on target web servers.

This integration performs brute-force discovery including:
- Directory and file enumeration
- DNS subdomain enumeration
- Virtual host discovery
- AWS S3 bucket enumeration
- GCS bucket discovery

Scans for:
- Hidden web directories and files
- DNS subdomains
- Virtual hosts on shared servers
- Publicly accessible S3/GCS buckets
- Common backup and configuration files
"""

import subprocess
import json
import time
import os

def perform_gobuster_scan(url, wordlist="/usr/share/wordlists/dirb/common.txt", mode="dir", threads=10, timeout=10, status_codes="200,204,301,302,307,401,403"):
    """
    Perform Gobuster directory/file enumeration.

    Args:
        url (str): Target URL
        wordlist (str): Path to wordlist
        mode (str): Scan mode (dir, dns, vhost)
        threads (int): Number of threads
        timeout (int): Timeout in seconds
        status_codes (str): Status codes to consider valid

    Returns:
        dict: Scan results
    """
    try:
        print(f"\nRunning Gobuster {mode} scan on {url}...")

        cmd = [
            'gobuster',
            mode,
            '-u', url,
            '-w', wordlist,
            '-t', str(threads),
            '-o', '/dev/stdout',  # Output to stdout
            '--timeout', f'{timeout}s',
            '-s', status_codes,
            '--no-error',  # Don't show errors
            '-q'  # Quiet mode
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        if result.returncode == 0:
            # Parse the output
            lines = result.stdout.strip().split('\n')
            found_items = []

            for line in lines:
                if line.strip() and not line.startswith('==============================================================='):
                    parts = line.split()
                    if len(parts) >= 2:
                        status_code = parts[0].strip('(Status: )')
                        item = parts[1]
                        found_items.append({
                            "url": item,
                            "status_code": status_code
                        })

            return {
                "found_items": found_items,
                "count": len(found_items),
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
        print("Gobuster not installed. Skipping Gobuster scan.")
        return None
    except subprocess.TimeoutExpired:
        print("Gobuster scan timed out.")
        return {"error": "Timeout", "success": False, "timestamp": time.time()}
    except Exception as e:
        print(f"Error during Gobuster scan: {e}")
        return {"error": str(e), "success": False, "timestamp": time.time()}

def gobuster_directory_scan(url, wordlist=None, extensions=None, threads=10):
    """
    Directory busting with Gobuster.

    Args:
        url (str): Target URL
        wordlist (str): Wordlist path
        extensions (str): File extensions to check (comma-separated)
        threads (int): Number of threads

    Returns:
        dict: Directory scan results
    """
    if not wordlist:
        # Try common wordlist locations
        common_wordlists = [
            "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt",
            "/usr/share/wordlists/dirb/common.txt",
            "/usr/share/seclists/Discovery/Web-Content/common.txt"
        ]
        for wl in common_wordlists:
            if os.path.exists(wl):
                wordlist = wl
                break

        if not wordlist:
            return {"error": "No wordlist found", "success": False}

    cmd_args = {
        "url": url,
        "wordlist": wordlist,
        "mode": "dir",
        "threads": threads
    }

    if extensions:
        # Note: Gobuster uses -x for extensions
        cmd_args["extensions"] = extensions

    return perform_gobuster_scan(**cmd_args)

def gobuster_dns_scan(domain, wordlist="/usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt", resolver="8.8.8.8"):
    """
    DNS subdomain enumeration with Gobuster.

    Args:
        domain (str): Target domain
        wordlist (str): Subdomain wordlist
        resolver (str): DNS resolver

    Returns:
        dict: DNS scan results
    """
    try:
        cmd = [
            'gobuster',
            'dns',
            '-d', domain,
            '-w', wordlist,
            '-r', resolver,
            '-o', '/dev/stdout',
            '--no-error',
            '-q'
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            found_subdomains = []

            for line in lines:
                if line.strip() and 'Found:' in line:
                    parts = line.split('Found: ')
                    if len(parts) > 1:
                        subdomain = parts[1].strip()
                        found_subdomains.append(subdomain)

            return {
                "found_subdomains": found_subdomains,
                "count": len(found_subdomains),
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

    except Exception as e:
        print(f"Error during Gobuster DNS scan: {e}")
        return {"error": str(e), "success": False, "timestamp": time.time()}
