"""
CrackMapExec network exploitation integration for the Dynamic Analysis Agent.

CrackMapExec (a.k.a CME) is a post-exploitation tool that helps automate
assessing the security of large Active Directory networks.

This integration performs Active Directory exploitation including:
- SMB password spraying and cracking
- LDAP enumeration and attacks
- Kerberos attacks and golden ticket creation
- MSSQL database exploitation
- RDP and WinRM lateral movement
- Credential harvesting and dumping

Used for:
- Active Directory penetration testing
- Lateral movement within networks
- Credential harvesting
- Domain compromise assessment
"""

import subprocess
import time

def perform_cme_smb_enum(target, username=None, password=None, domain=None):
    """
    Perform SMB enumeration with CrackMapExec.

    Args:
        target (str): Target IP/range or hostname
        username (str): Username for authentication
        password (str): Password for authentication
        domain (str): Domain name

    Returns:
        dict: Enumeration results
    """
    try:
        print(f"\nRunning CrackMapExec SMB enumeration on {target}...")

        # Build command
        cmd = ['crackmapexec', 'smb', target]

        if username and password:
            if domain:
                cmd.extend(['-u', f'{domain}\\{username}', '-p', password])
            else:
                cmd.extend(['-u', username, '-p', password])

        # Add enumeration modules
        cmd.extend(['--shares', '--users', '--groups', '--local-groups', '--sessions', '--loggedon-users'])

        print(f"Running command: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )

        if result.returncode == 0:
            print("CrackMapExec SMB enumeration completed.")

            # Parse results
            lines = result.stdout.split('\n')
            successful_auths = []
            shares = []
            users = []
            groups = []

            for line in lines:
                line = line.strip()
                if '[+]' in line:
                    if 'SMB' in line and 'authenticated' in line.lower():
                        successful_auths.append(line)
                    elif 'Share' in line:
                        shares.append(line)
                    elif 'User' in line:
                        users.append(line)
                    elif 'Group' in line:
                        groups.append(line)

            return {
                "output": result.stdout,
                "target": target,
                "successful_authentications": successful_auths,
                "shares": shares,
                "users": users,
                "groups": groups,
                "auth_count": len(successful_auths),
                "share_count": len(shares),
                "user_count": len(users),
                "group_count": len(groups),
                "success": True,
                "timestamp": time.time()
            }
        else:
            print(f"CrackMapExec SMB enumeration failed: {result.stderr}")
            return {
                "error": result.stderr,
                "target": target,
                "success": False,
                "timestamp": time.time()
            }

    except FileNotFoundError:
        print("CrackMapExec not installed. Skipping AD exploitation.")
        return None
    except subprocess.TimeoutExpired:
        print("CrackMapExec timed out.")
        return {
            "error": "Timeout",
            "target": target,
            "success": False,
            "timestamp": time.time()
        }
    except Exception as e:
        print(f"Error during CrackMapExec: {e}")
        return {
            "error": str(e),
            "target": target,
            "success": False,
            "timestamp": time.time()
        }

def perform_cme_pass_spray(target, username_file, password, domain=None):
    """
    Perform password spraying with CrackMapExec.

    Args:
        target (str): Target domain controller
        username_file (str): File containing usernames
        password (str): Password to spray
        domain (str): Domain name

    Returns:
        dict: Password spraying results
    """
    try:
        print(f"\nRunning CrackMapExec password spray on {target}...")

        cmd = ['crackmapexec', 'smb', target, '-u', username_file, '-p', password]

        if domain:
            cmd.extend(['-d', domain])

        cmd.append('--continue-on-success')

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=900  # 15 minute timeout for spraying
        )

        successful_sprays = []
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if '[+]' in line and 'SMB' in line:
                    successful_sprays.append(line.strip())

        return {
            "output": result.stdout,
            "target": target,
            "successful_sprays": successful_sprays,
            "spray_count": len(successful_sprays),
            "password": password,
            "success": True,
            "timestamp": time.time()
        }

    except Exception as e:
        print(f"Error during password spraying: {e}")
        return {
            "error": str(e),
            "target": target,
            "success": False,
            "timestamp": time.time()
        }
