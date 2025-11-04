"""
FFUF (Fuzz Faster U Fool) integration for the Dynamic Analysis Agent.

FFUF is a fast web fuzzer written in Go that allows typical directory discovery,
parameter fuzzing, and various other web application security testing tasks.

This integration performs web application fuzzing and discovery including:
- Directory and file enumeration
- Parameter fuzzing and discovery
- Virtual host scanning
- GET/POST parameter testing
- Custom wordlist support

Scans for:
- Hidden directories and files
- Backup files and configurations
- Parameter-based vulnerabilities
- Virtual host misconfigurations
- Common web application paths
"""

import subprocess
import json
import time
import os

def perform_ffuf_scan(url, wordlist="/usr/share/wordlists/dirb/common.txt", method="GET", data=None, headers=None, filters=None, threads=40, timeout=10):
    """
    Perform FFUF fuzzing scan.

    Args:
        url (str): Target URL with FUZZ placeholder
        wordlist (str): Path to wordlist
        method (str): HTTP method
        data (str): POST data
        headers (dict): HTTP headers
        filters (dict): Response filters
        threads (int): Number of threads
        timeout (int): Timeout per request

    Returns:
        dict: Scan results
    """
    try:
        print(f"\nRunning FFUF scan on {url}...")

        cmd = [
            'ffuf',
            '-u', url,
            '-w', wordlist,
            '-t', str(threads),
            '-timeout', str(timeout),
            '-o', '/dev/stdout',
            '-of', 'json',
            '-s'  # Silent mode
        ]

        if method != "GET":
            cmd.extend(['-X', method])

        if data:
            cmd.extend(['-d', data])

        if headers:
            for key, value in headers.items():
                cmd.extend(['-H', f'{key}: {value}'])

        if filters:
            if 'status' in filters:
                cmd.extend(['-fc', ','.join(map(str, filters['status']))])  # Filter out status codes
            if 'size' in filters:
                cmd.extend(['-fs', str(filters['size'])])  # Filter size

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)

        if result.returncode == 0:
            try:
                output_data = json.loads(result.stdout)
                results = output_data.get('results', [])

                return {
                    "results": results,
                    "count": len(results),
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
        print("FFUF not installed. Skipping FFUF scan.")
        return None
    except subprocess.TimeoutExpired:
        print("FFUF scan timed out.")
        return {"error": "Timeout", "success": False, "timestamp": time.time()}
    except Exception as e:
        print(f"Error during FFUF scan: {e}")
        return {"error": str(e), "success": False, "timestamp": time.time()}

def ffuf_directory_fuzz(url, wordlist=None, extensions=None, threads=40):
    """
    Directory and file fuzzing with FFUF.

    Args:
        url (str): Base URL (should end with /FUZZ)
        wordlist (str): Wordlist path
        extensions (list): File extensions to try
        threads (int): Number of threads

    Returns:
        dict: Directory fuzz results
    """
    if not wordlist:
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

    target_url = url.rstrip('/') + '/FUZZ'

    cmd_args = {
        "url": target_url,
        "wordlist": wordlist,
        "threads": threads
    }

    if extensions:
        # FFUF uses -e for extensions
        ext_wordlist = wordlist + ',' + ','.join(extensions)
        cmd_args["wordlist"] = ext_wordlist

    return perform_ffuf_scan(**cmd_args)

def ffuf_parameter_fuzz(url, parameters, wordlist="/usr/share/seclists/Fuzzing/params.txt", threads=40):
    """
    Parameter fuzzing with FFUF.

    Args:
        url (str): URL with parameter placeholder
        parameters (list): Parameters to fuzz
        wordlist (str): Parameter wordlist
        threads (int): Number of threads

    Returns:
        dict: Parameter fuzz results
    """
    # For parameter discovery, URL should have FUZZ in query or body
    return perform_ffuf_scan(url, wordlist, threads=threads)

def ffuf_subdomain_fuzz(domain, wordlist="/usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt", threads=40):
    """
    Subdomain fuzzing with FFUF.

    Args:
        domain (str): Domain with FUZZ placeholder (e.g., FUZZ.example.com)
        wordlist (str): Subdomain wordlist
        threads (int): Number of threads

    Returns:
        dict: Subdomain fuzz results
    """
    target_url = f"https://{domain}"

    # Filter out common false positives
    filters = {
        "status": [400, 404, 410]
    }

    return perform_ffuf_scan(target_url, wordlist, threads=threads, filters=filters)
