"""
Recon-ng web reconnaissance integration for the Dynamic Analysis Agent.

Recon-ng is a full-featured Web Reconnaissance framework written in Python.
It provides a powerful environment in which open source web-based reconnaissance
can be conducted quickly and thoroughly.

This integration performs comprehensive web reconnaissance including:
- DNS enumeration and resolution
- WHOIS lookups and analysis
- Google dorking for subdomain discovery
- Shodan integration for device discovery
- Social media profiling
- Contact information gathering
- Report generation and export

Used for:
- Comprehensive target reconnaissance
- Information gathering for security assessments
- Attack surface mapping
- Intelligence collection
"""

import subprocess
import time
import os

def perform_recon_ng_scan(domain, modules=None, workspace=None):
    """
    Perform Recon-ng reconnaissance scan.

    Args:
        domain (str): Target domain
        modules (list): List of recon modules to run
        workspace (str): Recon-ng workspace name

    Returns:
        dict: Reconnaissance results
    """
    try:
        print(f"\nRunning Recon-ng on {domain}...")

        # Create temporary resource script
        script_content = f"""
workspace -a {workspace or 'temp_workspace'}
db insert domains
{domain}
"""

        if modules:
            for module in modules:
                script_content += f"use {module}\nrun\n"
        else:
            # Default modules for comprehensive recon
            default_modules = [
                'recon/domains-hosts/bing_domain_web',
                'recon/domains-hosts/google_site_web',
                'recon/domains-hosts/shodan_hostname',
                'recon/hosts-hosts/resolve',
                'recon/hosts-hosts/reverse_resolve',
                'recon/domains-contacts/whois_pocs',
                'recon/domains-credentials/pwnedlist/account_creds'
            ]
            for module in default_modules:
                script_content += f"use {module}\nrun\n"

        script_content += "db query select * from hosts\n"
        script_content += "db query select * from contacts\n"
        script_content += "exit\n"

        script_file = f"recon_script_{int(time.time())}.rc"
        with open(script_file, 'w') as f:
            f.write(script_content)

        # Run recon-ng with script
        cmd = ['recon-ng', '-r', script_file]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=1200  # 20 minute timeout for comprehensive recon
        )

        # Clean up script file
        if os.path.exists(script_file):
            os.remove(script_file)

        if result.returncode == 0:
            print("Recon-ng scan completed.")

            # Parse output for findings
            lines = result.stdout.split('\n')
            hosts = []
            contacts = []
            credentials = []

            parsing_hosts = False
            parsing_contacts = False
            parsing_creds = False

            for line in lines:
                line = line.strip()
                if 'HOSTS' in line and '[' in line:
                    parsing_hosts = True
                    parsing_contacts = False
                    parsing_creds = False
                elif 'CONTACTS' in line and '[' in line:
                    parsing_hosts = False
                    parsing_contacts = True
                    parsing_creds = False
                elif 'CREDENTIALS' in line and '[' in line:
                    parsing_hosts = False
                    parsing_contacts = False
                    parsing_creds = True
                elif parsing_hosts and line and not line.startswith('['):
                    hosts.append(line)
                elif parsing_contacts and line and not line.startswith('['):
                    contacts.append(line)
                elif parsing_creds and line and not line.startswith('['):
                    credentials.append(line)

            return {
                "output": result.stdout,
                "domain": domain,
                "hosts": hosts,
                "contacts": contacts,
                "credentials": credentials,
                "host_count": len(hosts),
                "contact_count": len(contacts),
                "credential_count": len(credentials),
                "modules_run": modules or default_modules,
                "success": True,
                "timestamp": time.time()
            }
        else:
            return {
                "error": result.stderr,
                "domain": domain,
                "success": False,
                "timestamp": time.time()
            }

    except FileNotFoundError:
        print("Recon-ng not installed. Skipping web reconnaissance.")
        return None
    except subprocess.TimeoutExpired:
        # Clean up
        if os.path.exists(script_file):
            os.remove(script_file)
        print("Recon-ng timed out.")
        return {
            "error": "Timeout",
            "domain": domain,
            "success": False,
            "timestamp": time.time()
        }
    except Exception as e:
        # Clean up
        if os.path.exists(script_file):
            os.remove(script_file)
        print(f"Error during Recon-ng scan: {e}")
        return {
            "error": str(e),
            "domain": domain,
            "success": False,
            "timestamp": time.time()
        }

def get_recon_ng_modules():
    """
    Get list of available Recon-ng modules.

    Returns:
        list: Available modules
    """
    try:
        result = subprocess.run(
            ['recon-ng', '--list'],
            capture_output=True,
            text=True,
            timeout=30
        )

        modules = []
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if '/' in line and not line.startswith(' '):
                    modules.append(line.strip())

        return modules

    except Exception:
        return []
