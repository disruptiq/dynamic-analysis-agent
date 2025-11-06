"""
Commix command injection integration for the Dynamic Analysis Agent.

Commix (short for [comm]and [i]njection e[x]ploiter) is an automated tool
written by Anastasios Stasinopoulos (@ancst) that can be used from web
security professionals to test web applications with the view to find bugs,
errors or vulnerabilities related to command injection attacks.

This integration performs command injection exploitation including:
- Classic OS command injection detection
- Blind command injection testing
- Time-based injection techniques
- File-based injection methods
- Result-based verification
- Multiple injection point detection

Used for:
- Command injection vulnerability testing
- Blind injection exploitation
- System command execution through web apps
- Automated exploitation workflows
"""

import subprocess
import time

def perform_commix_scan(base_url, vulnerable_param=None, method='GET', data=None):
    """
    Perform Commix command injection scan.

    Args:
        base_url (str): Target URL
        vulnerable_param (str): Specific parameter to test
        method (str): HTTP method
        data (str): POST data

    Returns:
        dict: Scan results
    """
    try:
        print(f"\nRunning Commix on {base_url}...")

        cmd = ['commix', '--url', base_url]

        if method.upper() == 'POST' and data:
            cmd.extend(['--data', data])

        if vulnerable_param:
            cmd.extend(['-p', vulnerable_param])

        # Add options for comprehensive testing
        cmd.extend(['--batch', '--level', '3', '--technique', 'c'])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )

        if result.returncode == 0:
            print("Commix scan completed.")

            # Parse output for findings
            lines = result.stdout.split('\n')
            injection_points = []
            commands_executed = []

            for line in lines:
                if 'parameter' in line.lower() and 'appears' in line.lower():
                    injection_points.append(line.strip())
                if 'executed' in line.lower() and 'command' in line.lower():
                    commands_executed.append(line.strip())

            return {
                "output": result.stdout,
                "base_url": base_url,
                "vulnerable_param": vulnerable_param,
                "method": method,
                "injection_points": injection_points,
                "commands_executed": commands_executed,
                "vulnerable": len(injection_points) > 0,
                "success": True,
                "timestamp": time.time()
            }
        else:
            return {
                "error": result.stderr,
                "base_url": base_url,
                "vulnerable_param": vulnerable_param,
                "vulnerable": False,
                "success": False,
                "timestamp": time.time()
            }

    except FileNotFoundError:
        print("Commix not installed. Skipping command injection testing.")
        return None
    except subprocess.TimeoutExpired:
        print("Commix timed out.")
        return {
            "error": "Timeout",
            "base_url": base_url,
            "success": False,
            "timestamp": time.time()
        }
    except Exception as e:
        print(f"Error during Commix scan: {e}")
        return {
            "error": str(e),
            "base_url": base_url,
            "success": False,
            "timestamp": time.time()
        }

def perform_commix_shell(base_url, vulnerable_param, command="whoami"):
    """
    Execute system command via Commix.

    Args:
        base_url (str): Target URL
        vulnerable_param (str): Vulnerable parameter
        command (str): Command to execute

    Returns:
        dict: Command execution results
    """
    try:
        print(f"\nExecuting command via Commix: {command}")

        cmd = ['commix', '--url', base_url, '-p', vulnerable_param, '--os-cmd', command, '--batch']

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        return {
            "output": result.stdout,
            "error": result.stderr,
            "base_url": base_url,
            "vulnerable_param": vulnerable_param,
            "command": command,
            "success": result.returncode == 0,
            "timestamp": time.time()
        }

    except Exception as e:
        return {
            "error": str(e),
            "base_url": base_url,
            "command": command,
            "success": False,
            "timestamp": time.time()
        }
