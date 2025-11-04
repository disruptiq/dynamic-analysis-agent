"""
Integration with external security tools for the Dynamic Analysis Agent.
"""

import subprocess
import time
import os
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
    """
    if not ZAPv2:
        return

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
        if alerts:
            print(f"\nZAP found {len(alerts)} alerts:")
            for alert in alerts[:10]:  # Show first 10
                print(f"  - {alert['alert']}: {alert['description']} (Risk: {alert['risk']})")
            if len(alerts) > 10:
                print(f"  ... and {len(alerts) - 10} more alerts")
        else:
            print("\nZAP scan completed: No alerts found.")

    except Exception as e:
        print(f"Error during ZAP scan: {e}")

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

def perform_nmap_scan(host, port):
    """
    Perform Nmap port scan.

    Args:
        host (str): Target host
        port (int): Target port
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
            print("Nmap scan results:")
            print(result.stdout)
        else:
            print(f"Nmap scan failed: {result.stderr}")
    except FileNotFoundError:
        print("Nmap not installed. Skipping port scan.")
    except subprocess.TimeoutExpired:
        print("Nmap scan timed out.")
    except Exception as e:
        print(f"Error during Nmap scan: {e}")

def perform_nikto_scan(base_url):
    """
    Perform Nikto web server scan.

    Args:
        base_url (str): Target URL
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
            print("Nikto scan results:")
            # Filter out some noise, show key findings
            lines = result.stdout.split('\n')
            findings = [line for line in lines if '+ ' in line and 'OSVDB' in line]
            if findings:
                for finding in findings[:10]:  # Show first 10
                    print(f"  {finding}")
                if len(findings) > 10:
                    print(f"  ... and {len(findings) - 10} more findings")
            else:
                print("  No significant findings.")
        else:
            print(f"Nikto scan failed: {result.stderr}")
    except FileNotFoundError:
        print("Nikto not installed. Skipping web server scan.")
    except subprocess.TimeoutExpired:
        print("Nikto scan timed out.")
    except Exception as e:
        print(f"Error during Nikto scan: {e}")
