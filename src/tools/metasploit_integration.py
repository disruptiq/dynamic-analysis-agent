"""
Metasploit Framework integration for the Dynamic Analysis Agent.

The Metasploit Framework is a penetration testing platform that enables security
researchers to develop and execute exploit code against remote target machines.

This integration provides access to Metasploit's extensive collection of exploits,
payloads, and auxiliary modules for penetration testing including:
- Exploit execution and payload delivery
- Auxiliary scanning modules
- Post-exploitation modules
- Custom exploit development

Scans for and exploits:
- Known software vulnerabilities
- Network service weaknesses
- System misconfigurations
- Protocol-level vulnerabilities
- Custom vulnerability proofs-of-concept
"""

import subprocess
import time
import os
import tempfile

def perform_metasploit_scan(target_host, target_port=None, module_type="auxiliary", module_name="scanner/portscan/tcp"):
    """
    Perform Metasploit scan using specified module.

    Args:
        target_host (str): Target host
        target_port (int): Target port (optional)
        module_type (str): Module type (auxiliary, exploit, payload, etc.)
        module_name (str): Module name

    Returns:
        dict: Scan results
    """
    try:
        print(f"\nRunning Metasploit {module_name} on {target_host}...")

        # Create a temporary rc file for msfconsole
        with tempfile.NamedTemporaryFile(mode='w', suffix='.rc', delete=False) as rc_file:
            rc_file.write(f"use {module_type}/{module_name}\n")
            rc_file.write(f"set RHOSTS {target_host}\n")
            if target_port:
                rc_file.write(f"set RPORT {target_port}\n")
            rc_file.write("set THREADS 10\n")
            rc_file.write("run\n")
            rc_file.write("exit\n")
            rc_path = rc_file.name

        # Run msfconsole with the rc file
        cmd = ['msfconsole', '-q', '-r', rc_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        # Clean up
        os.unlink(rc_path)

        if result.returncode == 0:
            return {
                "output": result.stdout,
                "stderr": result.stderr,
                "success": True,
                "timestamp": time.time()
            }
        else:
            return {
                "error": result.stderr,
                "stdout": result.stdout,
                "success": False,
                "return_code": result.returncode,
                "timestamp": time.time()
            }

    except FileNotFoundError:
        print("Metasploit (msfconsole) not installed. Skipping Metasploit scan.")
        return None
    except subprocess.TimeoutExpired:
        print("Metasploit scan timed out.")
        return {"error": "Timeout", "success": False, "timestamp": time.time()}
    except Exception as e:
        print(f"Error during Metasploit scan: {e}")
        return {"error": str(e), "success": False, "timestamp": time.time()}

def run_metasploit_exploit(target_host, exploit_module, payload=None, options=None):
    """
    Run a Metasploit exploit.

    Args:
        target_host (str): Target host
        exploit_module (str): Exploit module path (e.g., 'windows/smb/ms17_010_eternalblue')
        payload (str): Payload to use
        options (dict): Additional options

    Returns:
        dict: Exploit results
    """
    try:
        print(f"\nRunning Metasploit exploit {exploit_module} on {target_host}...")

        with tempfile.NamedTemporaryFile(mode='w', suffix='.rc', delete=False) as rc_file:
            rc_file.write(f"use exploit/{exploit_module}\n")
            rc_file.write(f"set RHOSTS {target_host}\n")

            if payload:
                rc_file.write(f"set PAYLOAD {payload}\n")

            if options:
                for key, value in options.items():
                    rc_file.write(f"set {key} {value}\n")

            rc_file.write("exploit -j\n")  # Run in background
            rc_file.write("sleep 10\n")    # Wait a bit
            rc_file.write("jobs\n")        # Check jobs
            rc_file.write("exit\n")
            rc_path = rc_file.name

        cmd = ['msfconsole', '-q', '-r', rc_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        os.unlink(rc_path)

        return {
            "output": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0,
            "return_code": result.returncode,
            "timestamp": time.time()
        }

    except Exception as e:
        print(f"Error during Metasploit exploit: {e}")
        return {"error": str(e), "success": False, "timestamp": time.time()}

def check_msfconsole_available():
    """
    Check if Metasploit console is available.

    Returns:
        bool: True if available
    """
    try:
        result = subprocess.run(['msfconsole', '--version'], capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except:
        return False
