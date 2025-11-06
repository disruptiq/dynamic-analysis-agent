"""
ZMap internet-wide scanning integration for the Dynamic Analysis Agent.

ZMap is a fast single packet network scanner designed for Internet-wide network
surveys. On a typical desktop computer with a gigabit Ethernet connection,
ZMap is capable of scanning the entire public IPv4 address space in under 45 minutes.

This integration performs internet-scale network scanning including:
- High-speed IPv4 address space scanning
- Custom port scanning
- IPv6 scanning capabilities
- Output filtering and processing
- Rate limiting and performance tuning
- Integration with other analysis tools

Used for:
- Internet-wide reconnaissance
- Large-scale network surveys
- Port scanning at scale
- Network research and analysis
"""

import subprocess
import time

def perform_zmap_scan(target_network=None, port=80, output_file=None, bandwidth='10M'):
    """
    Perform ZMap internet-wide scan.

    Args:
        target_network (str): Target network in CIDR notation (e.g., 192.168.1.0/24)
        port (int): Port to scan
        output_file (str): Output file for results
        bandwidth (str): Bandwidth limit (e.g., '10M', '100M')

    Returns:
        dict: Scan results
    """
    try:
        print(f"\nRunning ZMap scan on port {port}...")

        if not output_file:
            output_file = f"zmap_results_{int(time.time())}.csv"

        cmd = ['zmap', '-p', str(port), '-o', output_file, '-B', bandwidth]

        if target_network:
            cmd.extend(['--whitelist-file', target_network])

        # Add options for safe scanning
        cmd.extend(['--cooldown-time', '300', '--seed', str(int(time.time()))])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout for large scans
        )

        if result.returncode == 0:
            print("ZMap scan completed.")

            # Read results if output file exists
            scan_results = []
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        if line.strip():
                            parts = line.strip().split(',')
                            if len(parts) >= 2:
                                scan_results.append({
                                    'ip': parts[0],
                                    'port': parts[1],
                                    'timestamp': parts[2] if len(parts) > 2 else None
                                })

            return {
                "output": result.stdout,
                "output_file": output_file,
                "target_network": target_network,
                "port": port,
                "bandwidth": bandwidth,
                "scan_results": scan_results,
                "host_count": len(scan_results),
                "success": True,
                "timestamp": time.time()
            }
        else:
            return {
                "error": result.stderr,
                "target_network": target_network,
                "port": port,
                "success": False,
                "timestamp": time.time()
            }

    except FileNotFoundError:
        print("ZMap not installed. Skipping internet-wide scanning.")
        return None
    except subprocess.TimeoutExpired:
        print("ZMap scan timed out.")
        return {
            "error": "Timeout",
            "target_network": target_network,
            "port": port,
            "success": False,
            "timestamp": time.time()
        }
    except Exception as e:
        print(f"Error during ZMap scan: {e}")
        return {
            "error": str(e),
            "target_network": target_network,
            "port": port,
            "success": False,
            "timestamp": time.time()
        }

def perform_zmap_port_scan(target_network, ports=[80, 443, 22, 3389], output_file=None):
    """
    Perform multi-port ZMap scan.

    Args:
        target_network (str): Target network
        ports (list): List of ports to scan
        output_file (str): Output file

    Returns:
        dict: Multi-port scan results
    """
    all_results = []

    for port in ports:
        result = perform_zmap_scan(target_network, port, f"{output_file}_{port}.csv" if output_file else None)
        if result:
            all_results.append(result)

    return {
        "scans": all_results,
        "total_hosts": sum(r.get('host_count', 0) for r in all_results if r.get('success')),
        "ports_scanned": ports,
        "target_network": target_network,
        "success": True,
        "timestamp": time.time()
    }
