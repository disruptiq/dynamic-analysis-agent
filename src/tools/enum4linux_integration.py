"""
Enum4linux SMB enumeration integration for the Dynamic Analysis Agent.

Enum4linux is a tool for enumerating information from Windows and Samba systems.

This integration performs SMB/Windows enumeration including:
- User enumeration
- Group enumeration
- Share enumeration
- Password policy information
- Domain/Workgroup information
- Printer information
- RID cycling for user discovery

Used for:
- Network reconnaissance on Windows/Samba systems
- User and group discovery
- Share enumeration for lateral movement
- Identifying weak configurations
"""

import subprocess
import time

def perform_enum4linux_scan(target, username=None, password=None, domain=None):
    """
    Perform Enum4linux SMB enumeration.

    Args:
        target (str): Target IP or hostname
        username (str): Username for authenticated enumeration
        password (str): Password for authenticated enumeration
        domain (str): Domain/workgroup name

    Returns:
        dict: Enumeration results or None if failed
    """
    try:
        print(f"\nRunning Enum4linux on {target}...")

        # Build command - use all enumeration options
        cmd = ['enum4linux', '-a', target]  # -a for all enumeration

        if username and password:
            cmd.extend(['-u', username, '-p', password])

        if domain:
            cmd.extend(['-d', domain])

        print(f"Running command: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        if result.returncode == 0:
            print("Enum4linux scan completed.")
            # Parse output for key findings
            lines = result.stdout.split('\n')

            users = []
            groups = []
            shares = []

            parsing_users = False
            parsing_groups = False
            parsing_shares = False

            for line in lines:
                line = line.strip()
                if 'user:' in line.lower():
                    parsing_users = True
                    parsing_groups = False
                    parsing_shares = False
                elif 'group:' in line.lower():
                    parsing_users = False
                    parsing_groups = True
                    parsing_shares = False
                elif 'share:' in line.lower():
                    parsing_users = False
                    parsing_groups = False
                    parsing_shares = True
                elif parsing_users and line and not line.startswith('['):
                    users.append(line.split()[0] if line.split() else line)
                elif parsing_groups and line and not line.startswith('['):
                    groups.append(line.split()[0] if line.split() else line)
                elif parsing_shares and line and not line.startswith('['):
                    shares.append(line.split()[0] if line.split() else line)

            return {
                "output": result.stdout,
                "target": target,
                "users": list(set(users)),  # Remove duplicates
                "groups": list(set(groups)),
                "shares": list(set(shares)),
                "user_count": len(set(users)),
                "group_count": len(set(groups)),
                "share_count": len(set(shares)),
                "success": True,
                "timestamp": time.time()
            }
        else:
            print(f"Enum4linux failed: {result.stderr}")
            return {
                "error": result.stderr,
                "target": target,
                "success": False,
                "timestamp": time.time()
            }

    except FileNotFoundError:
        print("Enum4linux not installed. Skipping SMB enumeration.")
        return None
    except subprocess.TimeoutExpired:
        print("Enum4linux timed out.")
        return {
            "error": "Timeout",
            "target": target,
            "success": False,
            "timestamp": time.time()
        }
    except Exception as e:
        print(f"Error during Enum4linux scan: {e}")
        return {
            "error": str(e),
            "target": target,
            "success": False,
            "timestamp": time.time()
        }
