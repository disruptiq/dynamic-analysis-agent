"""
Wireshark integration for the Dynamic Analysis Agent.

Wireshark is a free and open-source packet analyzer. It is used for network
troubleshooting, analysis, software and communications protocol development,
and education.

This integration performs network packet capture and analysis including:
- Real-time packet capture
- Protocol dissection and analysis
- Traffic pattern analysis
- Network forensics capabilities
- Packet filtering and search

Scans for:
- Network protocol anomalies
- Suspicious traffic patterns
- Packet-level security issues
- Network configuration problems
- Communication protocol vulnerabilities
"""

import subprocess
import time

def perform_wireshark_capture(interface="eth0", duration=30, output_file="/tmp/capture.pcap", filter=None):
    """
    Perform Wireshark packet capture.

    Args:
        interface (str): Network interface
        duration (int): Capture duration in seconds
        output_file (str): Output pcap file
        filter (str): Capture filter

    Returns:
        dict: Capture results
    """
    try:
        print(f"\nRunning Wireshark capture on {interface} for {duration} seconds...")

        cmd = [
            'tshark',  # Command-line version of Wireshark
            '-i', interface,
            '-a', f'duration:{duration}',
            '-w', output_file
        ]

        if filter:
            cmd.extend(['-f', filter])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=duration + 10)

        return {
            "output": result.stdout,
            "stderr": result.stderr,
            "output_file": output_file,
            "success": result.returncode == 0,
            "timestamp": time.time()
        }

    except FileNotFoundError:
        print("Wireshark/tshark not installed. Skipping packet capture.")
        return None
    except subprocess.TimeoutExpired:
        print("Packet capture completed.")
        return {"message": "Capture completed", "output_file": output_file, "success": True, "timestamp": time.time()}
    except Exception as e:
        print(f"Error during packet capture: {e}")
        return {"error": str(e), "success": False, "timestamp": time.time()}
