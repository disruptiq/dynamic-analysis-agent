"""
Proxychains proxy chaining integration for the Dynamic Analysis Agent.

Proxychains is a tool that forces any TCP connection made by any given
application to follow through proxy like TOR or any other SOCKS4,
SOCKS5 or HTTP(S) proxy.

This integration performs proxy chaining including:
- TCP connection redirection through proxies
- Support for SOCKS4/SOCKS5/HTTP proxies
- TOR integration
- Chain multiple proxies
- Anonymized network traffic

Used for:
- Anonymizing scanning activities
- Bypassing network restrictions
- TOR network integration
- Privacy during reconnaissance
"""

import subprocess
import time
import os

def perform_proxychains_command(command, proxy_config=None, use_tor=False):
    """
    Execute command through proxychains.

    Args:
        command (str): Command to execute through proxy chain
        proxy_config (str): Path to proxychains config file
        use_tor (bool): Use TOR as proxy

    Returns:
        dict: Command execution results
    """
    try:
        print(f"\nExecuting command through proxychains: {command}")

        cmd = ['proxychains']

        if proxy_config:
            cmd.extend(['-f', proxy_config])

        if use_tor:
            cmd.append('-q')  # quiet mode for TOR

        # Split command string into list
        cmd.extend(command.split())

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        return {
            "output": result.stdout,
            "error": result.stderr,
            "command": command,
            "proxy_config": proxy_config,
            "use_tor": use_tor,
            "success": result.returncode == 0,
            "timestamp": time.time()
        }

    except FileNotFoundError:
        print("Proxychains not installed. Skipping proxy execution.")
        return None
    except subprocess.TimeoutExpired:
        print("Proxychains command timed out.")
        return {
            "error": "Timeout",
            "command": command,
            "success": False,
            "timestamp": time.time()
        }
    except Exception as e:
        print(f"Error executing through proxychains: {e}")
        return {
            "error": str(e),
            "command": command,
            "success": False,
            "timestamp": time.time()
        }

def create_proxychains_config(proxy_list, output_file=None):
    """
    Create a proxychains configuration file.

    Args:
        proxy_list (list): List of proxy strings (e.g., ['socks5 127.0.0.1 9050'])
        output_file (str): Path to output config file

    Returns:
        str: Path to created config file
    """
    if not output_file:
        output_file = f"proxychains_{int(time.time())}.conf"

    config_content = """# Proxychains configuration
strict_chain
proxy_dns
remote_dns_subnet 224
tcp_read_time_out 15000
tcp_connect_time_out 8000

[ProxyList]
"""

    for proxy in proxy_list:
        config_content += proxy + "\n"

    with open(output_file, 'w') as f:
        f.write(config_content)

    return output_file

def perform_proxychains_nmap(target, proxy_config=None, use_tor=False):
    """
    Perform Nmap scan through proxychains.

    Args:
        target (str): Target to scan
        proxy_config (str): Proxychains config file
        use_tor (bool): Use TOR

    Returns:
        dict: Nmap scan results
    """
    nmap_cmd = f"nmap -sV -p 1-1000 {target}"
    return perform_proxychains_command(nmap_cmd, proxy_config, use_tor)
