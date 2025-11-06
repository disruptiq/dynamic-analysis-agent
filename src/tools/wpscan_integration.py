"""
WPScan integration for the Dynamic Analysis Agent.

WPScan is a black box WordPress vulnerability scanner that can be used to scan
remote WordPress installations to find security issues.

This integration performs WordPress-specific security testing including:
- WordPress version detection
- Plugin and theme vulnerability scanning
- User enumeration
- Configuration issue detection
- Known vulnerability detection

Scans for:
- Outdated WordPress core, plugins, and themes
- Vulnerable plugins and themes
- Misconfigured WordPress installations
- Exposed sensitive information
- User enumeration vulnerabilities
"""

import subprocess
import time

def perform_wpscan_scan(base_url, enumerate_users=False, enumerate_plugins=False, api_token=None):
    """
    Perform WPScan security scan on WordPress installation.

    Args:
        base_url (str): Target WordPress URL
        enumerate_users (bool): Whether to enumerate users
        enumerate_plugins (bool): Whether to enumerate plugins
        api_token (str): WPScan API token for vulnerability database

    Returns:
        dict: Scan results or None if failed
    """
    try:
        print(f"\nRunning WPScan on {base_url}...")

        # Build command
        cmd = ['wpscan', '--url', base_url, '--format', 'json']

        if api_token:
            cmd.extend(['--api-token', api_token])

        if enumerate_users:
            cmd.append('--enumerate')
            cmd.append('u')

        if enumerate_plugins:
            if '--enumerate' not in cmd:
                cmd.append('--enumerate')
            cmd.append('p')

        # Add other common options
        cmd.extend(['--random-user-agent', '--disable-tls-checks'])

        print(f"Running command: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout for comprehensive scans
        )

        if result.returncode == 0:
            print("WPScan completed successfully.")
            # Parse JSON output
            import json
            try:
                scan_data = json.loads(result.stdout)
                return {
                    "output": scan_data,
                    "version": scan_data.get('version', {}).get('number'),
                    "vulnerabilities": scan_data.get('vulnerabilities', []),
                    "interesting_findings": scan_data.get('interesting_findings', []),
                    "users": scan_data.get('users', []) if enumerate_users else [],
                    "plugins": scan_data.get('plugins', []) if enumerate_plugins else [],
                    "success": True,
                    "timestamp": time.time()
                }
            except json.JSONDecodeError:
                # Fallback to text output
                return {
                    "output": result.stdout,
                    "raw_output": result.stdout,
                    "success": True,
                    "timestamp": time.time()
                }
        else:
            print(f"WPScan failed: {result.stderr}")
            return {
                "error": result.stderr,
                "success": False,
                "timestamp": time.time()
            }

    except FileNotFoundError:
        print("WPScan not installed. Skipping WordPress scan.")
        return None
    except subprocess.TimeoutExpired:
        print("WPScan timed out.")
        return {
            "error": "Timeout",
            "success": False,
            "timestamp": time.time()
        }
    except Exception as e:
        print(f"Error during WPScan: {e}")
        return {
            "error": str(e),
            "success": False,
            "timestamp": time.time()
        }

def detect_wordpress(base_url):
    """
    Quick check if target is a WordPress installation.

    Args:
        base_url (str): Target URL

    Returns:
        bool: True if WordPress detected
    """
    try:
        import requests
        response = requests.get(f"{base_url}/wp-login.php", timeout=10)
        return response.status_code == 200
    except:
        return False
