"""
tcpdump integration for the Dynamic Analysis Agent.

Tcpdump is a powerful command-line packet analyzer that allows users to
capture and display TCP/IP and other packets being transmitted or received
over a network to which the computer is attached.

This integration performs command-line packet capture and analysis including:
- Raw packet capture capabilities
- Flexible filtering options
- Protocol-specific analysis
- Traffic monitoring and logging
- Network debugging support

Scans for:
- Packet-level network traffic
- Protocol-specific issues
- Network connectivity problems
- Traffic pattern analysis
- Security-related packet anomalies
"""

import subprocess
import time

def perform_tcpdump_capture(interface="eth0", duration=30, output_file="/tmp/tcpdump_capture.pcap", filter=None):
    """
    Perform tcpdump packet capture.

    Args:
        interface (str): Network interface
        duration (int): Capture duration in seconds
        output_file (str): Output pcap file
        filter (str): Capture filter

    Returns:
        dict: Capture results
    """
    try:
        print(f"\nRunning tcpdump capture on {interface} for {duration} seconds...")

        cmd = [
            'timeout', str(duration),
            'tcpdump',
            '-i', interface,
            '-w', output_file,
            '-U'  # Write packets immediately
        ]

        if filter:
            cmd.append(filter)

        result = subprocess.run(cmd, capture_output=True, text=True)

        return {
            "output": result.stdout,
            "stderr": result.stderr,
            "output_file": output_file,
            "success": result.returncode == 0,
            "timestamp": time.time()
        }

    except FileNotFoundError:
        print("tcpdump not installed. Skipping packet capture.")
        return None
    except Exception as e:
        print(f"Error during tcpdump capture: {e}")
        return {"error": str(e), "success": False, "timestamp": time.time()}
