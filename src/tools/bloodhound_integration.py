"""
BloodHound Active Directory reconnaissance integration for the Dynamic Analysis Agent.

BloodHound is a single page Javascript web application, built on top of Linkurious,
to help you make sense of the data. It uses graph theory to show you the shortest path
between you and a domain admin.

This integration performs Active Directory reconnaissance including:
- Domain user and group enumeration
- Computer and server discovery
- Group membership analysis
- Trust relationship mapping
- Attack path visualization
- Privilege escalation path identification

Used for:
- Active Directory security assessment
- Lateral movement path discovery
- Privilege escalation analysis
- Domain compromise assessment
"""

import subprocess
import time
import os
import json

def perform_bloodhound_collection(domain_controller=None, username=None, password=None, output_dir=None):
    """
    Perform BloodHound data collection.

    Args:
        domain_controller (str): Domain controller IP/hostname
        username (str): Domain username for collection
        password (str): Domain password
        output_dir (str): Directory to store collection results

    Returns:
        dict: Collection results
    """
    try:
        print(f"\nRunning BloodHound collection on domain {domain_controller or 'local'}...")

        if not output_dir:
            output_dir = f"bloodhound_{int(time.time())}"

        os.makedirs(output_dir, exist_ok=True)

        # BloodHound collection typically uses SharpHound or similar
        # For Python integration, we might use bloodhound-python
        # This is a simplified version assuming bloodhound-python is available

        cmd = ['bloodhound-python', '-c', 'All', '-d', domain_controller or '.']

        if username and password:
            cmd.extend(['-u', username, '-p', password])

        cmd.extend(['--output', output_dir])

        print(f"Running command: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=1800  # 30 minute timeout for large domains
        )

        if result.returncode == 0:
            print("BloodHound collection completed.")

            # List collected files
            collected_files = []
            if os.path.exists(output_dir):
                collected_files = os.listdir(output_dir)

            return {
                "output": result.stdout,
                "output_dir": output_dir,
                "collected_files": collected_files,
                "domain_controller": domain_controller,
                "success": True,
                "timestamp": time.time()
            }
        else:
            print(f"BloodHound collection failed: {result.stderr}")
            return {
                "error": result.stderr,
                "domain_controller": domain_controller,
                "success": False,
                "timestamp": time.time()
            }

    except FileNotFoundError:
        print("BloodHound Python not installed. Skipping AD reconnaissance.")
        return None
    except subprocess.TimeoutExpired:
        print("BloodHound collection timed out.")
        return {
            "error": "Timeout",
            "domain_controller": domain_controller,
            "success": False,
            "timestamp": time.time()
        }
    except Exception as e:
        print(f"Error during BloodHound collection: {e}")
        return {
            "error": str(e),
            "domain_controller": domain_controller,
            "success": False,
            "timestamp": time.time()
        }

def analyze_bloodhound_data(json_files):
    """
    Analyze collected BloodHound JSON data.

    Args:
        json_files (list): List of BloodHound JSON files to analyze

    Returns:
        dict: Analysis results
    """
    try:
        print(f"\nAnalyzing BloodHound data from {len(json_files)} files...")

        analysis = {
            "users": [],
            "groups": [],
            "computers": [],
            "domains": [],
            "ous": [],
            "gpos": []
        }

        for json_file in json_files:
            if os.path.exists(json_file) and json_file.endswith('.json'):
                try:
                    with open(json_file, 'r') as f:
                        data = json.load(f)

                    if 'users' in data:
                        analysis['users'].extend(data['users'])
                    if 'groups' in data:
                        analysis['groups'].extend(data['groups'])
                    if 'computers' in data:
                        analysis['computers'].extend(data['computers'])
                    if 'domains' in data:
                        analysis['domains'].extend(data['domains'])

                except json.JSONDecodeError:
                    continue

        return {
            "analysis": analysis,
            "total_users": len(analysis['users']),
            "total_groups": len(analysis['groups']),
            "total_computers": len(analysis['computers']),
            "total_domains": len(analysis['domains']),
            "success": True,
            "timestamp": time.time()
        }

    except Exception as e:
        print(f"Error analyzing BloodHound data: {e}")
        return {
            "error": str(e),
            "success": False,
            "timestamp": time.time()
        }
