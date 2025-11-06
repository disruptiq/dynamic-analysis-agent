"""
Chisel TCP/UDP tunneling integration for the Dynamic Analysis Agent.

Chisel is a fast TCP/UDP tunnel, transported over HTTP, secured via SSH.
Single executable including both client and server. Chisel is mainly useful for
passing through firewalls, though it can also be used to provide a secure
endpoint into your network.

This integration performs secure tunneling including:
- TCP/UDP port forwarding
- Reverse tunneling
- SOCKS5 proxy creation
- Encrypted tunnel establishment
- Firewall bypass capabilities

Used for:
- Secure remote access during testing
- Firewall evasion
- Encrypted communication channels
- Remote port forwarding
"""

import subprocess
import time
import threading

def perform_chisel_server(listen_port=8080, reverse=False):
    """
    Start Chisel server for tunneling.

    Args:
        listen_port (int): Port to listen on
        reverse (bool): Enable reverse tunneling

    Returns:
        dict: Server startup results
    """
    try:
        print(f"\nStarting Chisel server on port {listen_port}...")

        cmd = ['chisel', 'server', '-p', str(listen_port)]

        if reverse:
            cmd.append('--reverse')

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Give it a moment to start
        time.sleep(2)

        if process.poll() is None:
            print("Chisel server started successfully.")
            return {
                "process": process,
                "listen_port": listen_port,
                "reverse": reverse,
                "server_started": True,
                "success": True,
                "timestamp": time.time()
            }
        else:
            stdout, stderr = process.communicate()
            return {
                "error": stderr,
                "stdout": stdout,
                "listen_port": listen_port,
                "server_started": False,
                "success": False,
                "timestamp": time.time()
            }

    except FileNotFoundError:
        print("Chisel not installed. Skipping tunneling setup.")
        return None
    except Exception as e:
        print(f"Error starting Chisel server: {e}")
        return {
            "error": str(e),
            "listen_port": listen_port,
            "success": False,
            "timestamp": time.time()
        }

def perform_chisel_client(server_host, server_port=8080, local_port=None, remote_port=None):
    """
    Start Chisel client to connect to server.

    Args:
        server_host (str): Chisel server hostname/IP
        server_port (int): Chisel server port
        local_port (int): Local port to forward
        remote_port (int): Remote port to access

    Returns:
        dict: Client connection results
    """
    try:
        print(f"\nConnecting Chisel client to {server_host}:{server_port}...")

        cmd = ['chisel', 'client', f'{server_host}:{server_port}']

        if local_port and remote_port:
            cmd.append(f'R:{local_port}:{server_host}:{remote_port}')

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        time.sleep(3)

        if process.poll() is None:
            print("Chisel client connected successfully.")
            return {
                "process": process,
                "server_host": server_host,
                "server_port": server_port,
                "local_port": local_port,
                "remote_port": remote_port,
                "client_connected": True,
                "success": True,
                "timestamp": time.time()
            }
        else:
            stdout, stderr = process.communicate()
            return {
                "error": stderr,
                "stdout": stdout,
                "server_host": server_host,
                "server_port": server_port,
                "client_connected": False,
                "success": False,
                "timestamp": time.time()
            }

    except FileNotFoundError:
        print("Chisel not installed. Skipping tunneling connection.")
        return None
    except Exception as e:
        print(f"Error connecting Chisel client: {e}")
        return {
            "error": str(e),
            "server_host": server_host,
            "server_port": server_port,
            "success": False,
            "timestamp": time.time()
        }

def stop_chisel_process(process):
    """
    Stop a Chisel process.

    Args:
        process (subprocess.Popen): Chisel process to stop
    """
    if process:
        try:
            process.terminate()
            process.wait(timeout=10)
            print("Chisel process stopped.")
        except:
            process.kill()
