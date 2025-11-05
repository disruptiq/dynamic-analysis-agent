# Tool availability checking functionality

import subprocess
import concurrent.futures
import re
from colorama import Fore, Style, init


def check_tool_worker(tool_name):
    """Worker function to check a single tool's availability."""
    is_available, status = check_tool_availability(tool_name)
    return tool_name, is_available, status


def list_available_tools():
    """List all available security tools organized by category with availability status."""
    init(autoreset=True)
    tools_by_category = {
        "Dynamic Scanning Tools": [
            "ZAP (OWASP Zed Attack Proxy)",
            "Nmap",
            "Nikto"
        ],
        "Vulnerability Scanners": [
            "Nessus",
            "OpenVAS",
            "Acunetix",
            "QualysGuard",
            "Rapid7 Nexpose"
        ],
        "Exploitation Tools": [
            "Metasploit",
            "SQLMap"
        ],
        "Web Scanning Tools": [
            "Gobuster",
            "FFUF (Fuzz Faster U Fool)",
            "Nuclei",
            "Jaeles"
        ],
        "XSS Tools": [
            "XSStrike"
        ],
        "Parameter Discovery": [
            "Arjun"
        ],
        "Runtime Security": [
            "Falco",
            "OSSEC"
        ],
        "Network Security": [
            "Snort",
            "Suricata",
            "Wireshark",
            "TCPDump"
        ],
        "Browser Exploitation": [
            "BeEF (Browser Exploitation Framework)"
        ]
    }

    print("Security Tools Availability Check:")
    print("=" * 60)
    print("Checking tool availability in parallel...")

    # Collect all tools for parallel processing
    all_tools = []
    for tools in tools_by_category.values():
        all_tools.extend(tools)

    total_tools = len(all_tools)
    available_count = 0

    # Check all tools in parallel using ThreadPoolExecutor
    results = {}
    max_workers = min(8, len(all_tools))  # Don't use more workers than tools
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_tool = {executor.submit(check_tool_worker, tool): tool for tool in all_tools}

        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_tool):
            tool_name, is_available, status = future.result()
            results[tool_name] = (is_available, status)
            if is_available:
                available_count += 1

    # Display results organized by category
    print()
    for category, tools in tools_by_category.items():
        print(f"{category}:")
        for tool in tools:
            is_available, status = results[tool]
            if is_available:
                status_symbol = f"{Fore.GREEN}[OK]{Style.RESET_ALL}"
            else:
                status_symbol = f"{Fore.RED}[NO]{Style.RESET_ALL}"
            print(f"  {status_symbol} {tool} - {status}")
        print()

    print(f"Summary: {available_count}/{total_tools} tools available")
    print("\nLegend: [OK] Available  [NO] Not Available")


def check_tool_availability(tool_name):
    """
    Check if a security tool is available on the system.

    Args:
        tool_name (str): Name of the tool to check

    Returns:
        tuple: (is_available, status_message)
    """
    tool_checks = {
        "ZAP (OWASP Zed Attack Proxy)": check_zap_available,
        "Nmap": lambda: check_command_available("nmap"),
        "Nikto": lambda: check_command_available("nikto"),
        "Nessus": lambda: check_command_available("nessus"),
        "OpenVAS": lambda: check_command_available("openvas-start"),
        "Acunetix": lambda: check_command_available("acunetix"),
        "QualysGuard": lambda: check_command_available("qualys-api-scanner"),
        "Rapid7 Nexpose": lambda: check_command_available("nexpose"),
        "Metasploit": lambda: check_command_available("msfconsole"),
        "SQLMap": lambda: check_command_available("sqlmap"),
        "Gobuster": lambda: check_command_available("gobuster"),
        "FFUF (Fuzz Faster U Fool)": lambda: check_command_available("ffuf"),
        "Nuclei": lambda: check_command_available("nuclei"),
        "Jaeles": lambda: check_command_available("jaeles"),
        "XSStrike": lambda: check_command_available("xsstrike"),
        "Arjun": lambda: check_command_available("arjun"),
        "Falco": lambda: check_command_available("falco"),
        "OSSEC": lambda: check_command_available("ossec-control"),
        "Snort": lambda: check_command_available("snort"),
        "Suricata": lambda: check_command_available("suricata"),
        "Wireshark": lambda: check_command_available("tshark"),
        "TCPDump": lambda: check_command_available("tcpdump"),
        "BeEF (Browser Exploitation Framework)": lambda: check_command_available("beef")
    }

    check_func = tool_checks.get(tool_name)
    if check_func:
        try:
            return check_func()
        except Exception as e:
            return False, f"Error checking availability: {str(e)}"
    return False, "No availability check defined"


def check_command_available(command):
    """
    Check if a command is available in PATH.

    Args:
        command (str): Command to check

    Returns:
        tuple: (is_available, status_message)
    """
    try:
        # Use shorter timeout and simpler version check
        result = subprocess.run([command, "--version"],
                              capture_output=True,
                              text=True,
                              timeout=3,
                              input='\n')  # Provide newline input for interactive tools
        if result.returncode == 0:
            # Quick version extraction from first line
            version = ""
            if result.stdout and result.stdout.strip():
                first_line = result.stdout.strip().split('\n', 1)[0]
                # Extract version-like patterns (common formats)
                version_match = re.search(r'(\d+(?:\.\d+)+)', first_line)
                if version_match:
                    version = version_match.group(1)
            return True, f"v{version}" if version else "Available"
        else:
            return False, "Command failed"
    except FileNotFoundError:
        return False, "Not installed"
    except subprocess.TimeoutExpired:
        return False, "Timeout"
    except Exception as e:
        return False, f"Error"


def check_zap_available():
    """
    Check if ZAP is available (both Python module and executable).

    Returns:
        tuple: (is_available, status_message)
    """
    # Check Python module
    try:
        import zapv2
        module_available = True
    except ImportError:
        return False, "No module"

    # Check executable (faster check)
    try:
        result = subprocess.run(["zap.sh", "--version"],
                              capture_output=True,
                              text=True,
                              timeout=3)
        if result.returncode == 0:
            return True, "Available"
        else:
            return False, "Exec failed"
    except FileNotFoundError:
        return False, "No executable"
    except subprocess.TimeoutExpired:
        return False, "Timeout"
    except Exception:
        return False, "Error"
