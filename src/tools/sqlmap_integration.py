"""
SQLMap advanced integration for the Dynamic Analysis Agent.

SQLMap is an open-source penetration testing tool that automates the process of
detecting and exploiting SQL injection flaws and taking over of database servers.

This integration performs automated SQL injection testing and database exploitation including:
- Detection of SQL injection vulnerabilities
- Database fingerprinting and enumeration
- Data extraction from databases
- File system access and command execution
- Database takeover capabilities

Scans for and exploits:
- Various SQL injection techniques (union, error, blind, time-based)
- Database management system identification
- Database user privileges and roles
- Database structure and content dumping
- File system read/write capabilities
"""

import subprocess
import json
import time
import os
import tempfile

def perform_sqlmap_scan(url, method="GET", data=None, cookie=None, user_agent=None, level=1, risk=1, dbms=None):
    """
    Perform SQLMap injection testing.

    Args:
        url (str): Target URL
        method (str): HTTP method (GET, POST)
        data (str): POST data
        cookie (str): Cookie string
        user_agent (str): User agent string
        level (int): Test level (1-5)
        risk (int): Risk level (1-3)
        dbms (str): Target DBMS

    Returns:
        dict: Scan results
    """
    try:
        print(f"\nRunning SQLMap scan on {url}...")

        cmd = [
            'sqlmap',
            '-u', url,
            '--batch',  # Non-interactive mode
            '--json-output',  # JSON output
            f'--level={level}',
            f'--risk={risk}',
            '--technique=BEUSTQ',  # All techniques
            '--flush-session',  # Flush session data
            '--random-agent'  # Use random user agent
        ]

        if method == "POST" and data:
            cmd.extend(['--data', data])

        if cookie:
            cmd.extend(['--cookie', cookie])

        if user_agent:
            cmd.extend(['--user-agent', user_agent])

        if dbms:
            cmd.extend(['--dbms', dbms])

        # Create temporary directory for output
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, 'sqlmap_output.json')
            cmd.extend(['--output-dir', temp_dir])

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)  # 30 min timeout

            # Try to read JSON output
            json_results = {}
            if os.path.exists(output_file):
                try:
                    with open(output_file, 'r') as f:
                        json_results = json.load(f)
                except:
                    pass

            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "json_results": json_results,
                "success": result.returncode == 0,
                "return_code": result.returncode,
                "timestamp": time.time()
            }

    except FileNotFoundError:
        print("SQLMap not installed. Skipping SQLMap scan.")
        return None
    except subprocess.TimeoutExpired:
        print("SQLMap scan timed out.")
        return {"error": "Timeout", "success": False, "timestamp": time.time()}
    except Exception as e:
        print(f"Error during SQLMap scan: {e}")
        return {"error": str(e), "success": False, "timestamp": time.time()}

def sqlmap_dump_database(url, database_name, cookie=None):
    """
    Dump database using SQLMap.

    Args:
        url (str): Target URL
        database_name (str): Database to dump
        cookie (str): Cookie string

    Returns:
        dict: Dump results
    """
    try:
        print(f"Dumping database {database_name} from {url}...")

        cmd = [
            'sqlmap',
            '-u', url,
            '--batch',
            '--dump',
            '--dbms', database_name
        ]

        if cookie:
            cmd.extend(['--cookie', cookie])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)  # 1 hour timeout

        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0,
            "return_code": result.returncode,
            "timestamp": time.time()
        }

    except Exception as e:
        print(f"Error during SQLMap dump: {e}")
        return {"error": str(e), "success": False, "timestamp": time.time()}

def sqlmap_check_vulnerable(url, method="GET", data=None, cookie=None):
    """
    Quick vulnerability check with SQLMap.

    Args:
        url (str): Target URL
        method (str): HTTP method
        data (str): POST data
        cookie (str): Cookie string

    Returns:
        bool: True if vulnerable
    """
    try:
        result = perform_sqlmap_scan(url, method, data, cookie, level=1, risk=1)
        if result and result.get("success"):
            # Check if any injection was found
            json_results = result.get("json_results", {})
            if json_results and json_results.get("vulnerable"):
                return True
        return False
    except:
        return False
