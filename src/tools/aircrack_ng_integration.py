"""
Aircrack-ng wireless testing integration for the Dynamic Analysis Agent.

Aircrack-ng is a complete suite of tools to assess WiFi network security.
It focuses on different areas of WiFi security: monitoring, attacking,
testing, and cracking.

This integration performs wireless security testing including:
- Wireless network discovery and monitoring
- WEP/WPA cracking capabilities
- Handshake capture and analysis
- Deauthentication attacks
- Fake access point creation
- Wireless intrusion detection

Used for:
- Wireless network reconnaissance
- Security assessment of WiFi networks
- Capturing WPA handshakes for offline cracking
- Identifying weak wireless configurations
"""

import subprocess
import threading
import time
import os
import signal

def perform_aircrack_monitor(interface, duration=30):
    """
    Monitor wireless networks using Aircrack-ng.

    Args:
        interface (str): Wireless interface in monitor mode
        duration (int): Monitoring duration in seconds

    Returns:
        dict: Wireless monitoring results
    """
    try:
        print(f"\nMonitoring wireless networks on {interface} for {duration}s...")

        # Put interface in monitor mode
        subprocess.run(['airmon-ng', 'start', interface], capture_output=True)

        # Get monitor interface name
        monitor_interface = f"{interface}mon"

        # Start airodump-ng
        cmd = ['airodump-ng', monitor_interface, '-w', 'capture', '--output-format', 'csv']

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Wait for monitoring period
        time.sleep(duration)

        # Stop monitoring
        process.terminate()
        try:
            process.wait(timeout=10)
        except:
            process.kill()

        # Stop monitor mode
        subprocess.run(['airmon-ng', 'stop', monitor_interface], capture_output=True)

        # Read captured data
        csv_file = 'capture-01.csv'
        networks = []

        if os.path.exists(csv_file):
            with open(csv_file, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if ',' in line and not line.startswith('BSSID'):
                        parts = line.strip().split(',')
                        if len(parts) >= 14:
                            network = {
                                'bssid': parts[0].strip(),
                                'first_time_seen': parts[1].strip(),
                                'last_time_seen': parts[2].strip(),
                                'channel': parts[3].strip(),
                                'speed': parts[4].strip(),
                                'privacy': parts[5].strip(),
                                'cipher': parts[6].strip(),
                                'authentication': parts[7].strip(),
                                'power': parts[8].strip(),
                                'beacons': parts[9].strip(),
                                'iv': parts[10].strip(),
                                'lan_ip': parts[11].strip(),
                                'id_length': parts[12].strip(),
                                'essid': parts[13].strip() if len(parts) > 13 else ''
                            }
                            networks.append(network)

            # Clean up
            for f in ['capture-01.csv', 'capture-01.cap', 'capture-01.kismet.csv', 'capture-01.kismet.netxml']:
                if os.path.exists(f):
                    os.remove(f)

        return {
            "output": f"Monitored {len(networks)} wireless networks",
            "networks": networks,
            "network_count": len(networks),
            "interface": interface,
            "duration": duration,
            "success": True,
            "timestamp": time.time()
        }

    except FileNotFoundError:
        print("Aircrack-ng not installed. Skipping wireless testing.")
        return None
    except Exception as e:
        print(f"Error during wireless monitoring: {e}")
        return {
            "error": str(e),
            "interface": interface,
            "success": False,
            "timestamp": time.time()
        }

def perform_aircrack_wpa_crack(capture_file, wordlist=None):
    """
    Attempt WPA cracking on captured handshake.

    Args:
        capture_file (str): Path to capture file with handshake
        wordlist (str): Path to wordlist for cracking

    Returns:
        dict: Cracking results
    """
    try:
        print(f"\nAttempting WPA cracking on {capture_file}...")

        if not wordlist:
            wordlist = '/usr/share/wordlists/rockyou.txt'

        cmd = ['aircrack-ng', '-w', wordlist, '-b', capture_file]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout for cracking
        )

        if result.returncode == 0 and 'KEY FOUND' in result.stdout.upper():
            print("WPA key found!")
            return {
                "output": result.stdout,
                "key_found": True,
                "capture_file": capture_file,
                "success": True,
                "timestamp": time.time()
            }
        else:
            print("WPA cracking completed - key not found.")
            return {
                "output": result.stdout,
                "key_found": False,
                "capture_file": capture_file,
                "success": True,
                "timestamp": time.time()
            }

    except FileNotFoundError:
        print("Aircrack-ng not installed. Skipping WPA cracking.")
        return None
    except subprocess.TimeoutExpired:
        print("WPA cracking timed out.")
        return {
            "error": "Timeout",
            "capture_file": capture_file,
            "key_found": False,
            "success": False,
            "timestamp": time.time()
        }
    except Exception as e:
        print(f"Error during WPA cracking: {e}")
        return {
            "error": str(e),
            "capture_file": capture_file,
            "success": False,
            "timestamp": time.time()
        }
