"""
Suricata integration for the Dynamic Analysis Agent.

Suricata is a high-performance Network IDS, IPS and Network Security Monitoring
engine. It is open-source and owned by the Open Information Security Foundation (OISF).

This integration performs advanced network security monitoring including:
- Multi-threaded packet processing
- Advanced protocol analysis
- File extraction and analysis
- TLS inspection capabilities
- Lua scripting for custom detection

Scans for:
- Advanced persistent threats
- Zero-day attacks
- Encrypted traffic anomalies
- File-based malware
- Complex attack patterns
"""

import subprocess
import time

def perform_suricata_analysis(interface="eth0", config_file="/etc/suricata/suricata.yaml", duration=30):
    """
    Perform Suricata intrusion detection analysis.

    Args:
        interface (str): Network interface to monitor
        config_file (str): Suricata configuration file
        duration (int): Analysis duration in seconds

    Returns:
        dict: Analysis results
    """
    try:
        print(f"\nRunning Suricata analysis on {interface} for {duration} seconds...")

        cmd = [
            'suricata',
            '-c', config_file,
            '-i', interface,
            '--runmode', 'autofp'
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=duration)

        return {
            "output": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0,
            "timestamp": time.time()
        }

    except FileNotFoundError:
        print("Suricata not installed. Skipping Suricata analysis.")
        return None
    except subprocess.TimeoutExpired:
        print("Suricata analysis completed (timeout reached).")
        return {"message": "Analysis completed", "success": True, "timestamp": time.time()}
    except Exception as e:
        print(f"Error during Suricata analysis: {e}")
        return {"error": str(e), "success": False, "timestamp": time.time()}
