"""
OWASP ZAP (Zed Attack Proxy) integration for the Dynamic Analysis Agent.

OWASP ZAP is a free, open-source web application security scanner. It is designed
to be used by both those new to application security as well as professional penetration testers.

This integration performs comprehensive dynamic application security testing (DAST) including:
- Automated spidering and active scanning
- Passive scanning for security vulnerabilities
- Active scanning with attack vectors
- API scanning capabilities
- Authentication and session management testing

Scans for vulnerabilities such as:
- SQL Injection, XSS, CSRF, XXE, SSRF
- Broken authentication and session management
- Security misconfigurations
- Sensitive data exposure
- Broken access control
"""

import subprocess
import time

try:
    from zapv2 import ZAPv2
except ImportError:
    ZAPv2 = None

def start_zap(zap_port=8090):
    """
    Start OWASP ZAP in headless mode.

    Args:
        zap_port (int): Port for ZAP API

    Returns:
        subprocess.Popen: ZAP process
    """
    if not ZAPv2:
        print("ZAP not available, skipping ZAP integration.")
        return None

    try:
        # Assume ZAP is installed and zap.sh is in PATH
        zap_process = subprocess.Popen(
            ['zap.sh', '-daemon', '-port', str(zap_port), '-host', '0.0.0.0'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(10)  # Wait for ZAP to start
        return zap_process
    except FileNotFoundError:
        print("ZAP not installed or zap.sh not in PATH. Skipping ZAP integration.")
        return None
    except Exception as e:
        print(f"Error starting ZAP: {e}")
        return None

def perform_zap_scan(base_url, zap_port=8090):
    """
    Perform OWASP ZAP security scan.

    Args:
        base_url (str): Target URL to scan
        zap_port (int): ZAP API port

    Returns:
        dict: Scan results or None if failed
    """
    if not ZAPv2:
        return None

    try:
        zap = ZAPv2(apikey='changeme', proxies={'http': f'http://127.0.0.1:{zap_port}', 'https': f'http://127.0.0.1:{zap_port}'})

        print("\nStarting OWASP ZAP scan...")

        # Spider the site
        print("Running spider...")
        scan_id = zap.spider.scan(base_url)
        while int(zap.spider.status(scan_id)) < 100:
            time.sleep(1)

        # Perform active scan
        print("Running active scan...")
        scan_id = zap.ascan.scan(base_url)
        while int(zap.ascan.status(scan_id)) < 100:
            time.sleep(2)

        # Get alerts
        alerts = zap.core.alerts()
        print("ZAP scan completed.")

        return {
            "alerts": alerts,
            "alert_count": len(alerts),
            "success": True,
            "timestamp": time.time()
        }

    except Exception as e:
        print(f"Error during ZAP scan: {e}")
        return {
            "error": str(e),
            "success": False,
            "timestamp": time.time()
        }

def stop_zap(zap_process):
    """
    Stop the ZAP process.

    Args:
        zap_process (subprocess.Popen): ZAP process to stop
    """
    if zap_process:
        try:
            zap_process.terminate()
            zap_process.wait(timeout=10)
            print("ZAP stopped.")
        except Exception as e:
            print(f"Error stopping ZAP: {e}")
            zap_process.kill()
