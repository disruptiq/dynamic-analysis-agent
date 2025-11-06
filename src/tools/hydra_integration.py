"""
Hydra brute force integration for the Dynamic Analysis Agent.

Hydra is a parallelized login cracker which supports numerous protocols
to attack. It is very fast and flexible, and new modules are easy to add.

This integration performs brute force credential testing including:
- HTTP POST form brute forcing
- Basic authentication brute forcing
- Common service credential testing

Supports protocols:
- HTTP/HTTPS (form-based, basic auth)
- FTP, SSH, Telnet, SMB
- Databases (MySQL, PostgreSQL, etc.)
- And many more

Used for:
- Testing weak/default credentials
- Authentication bypass attempts
- Password policy validation
"""

import subprocess
import time

def perform_hydra_brute_force(target, port, service='http-post-form', username=None, password_list=None, extra_params=None):
    """
    Perform Hydra brute force attack.

    Args:
        target (str): Target host/IP
        port (int): Target port
        service (str): Service type (e.g., 'http-post-form', 'http-get', 'ftp')
        username (str): Username to test (or None for user list)
        password_list (str): Path to password list file
        extra_params (str): Additional Hydra parameters

    Returns:
        dict: Brute force results or None if failed
    """
    try:
        print(f"\nRunning Hydra brute force on {target}:{port}...")

        # Build command
        cmd = ['hydra', '-t', '4', '-f']  # -t threads, -f exit on first found

        if username:
            cmd.extend(['-l', username])
        else:
            # Use default user list if no username specified
            cmd.extend(['-L', '/usr/share/wordlists/metasploit/default_users_for_services_unhash.txt'])

        if password_list:
            cmd.extend(['-P', password_list])
        else:
            # Use default password list
            cmd.extend(['-P', '/usr/share/wordlists/rockyou.txt'])

        # Service specific
        if service == 'http-post-form':
            # Assume common login path, adjust as needed
            login_path = "/login"
            form_data = "username=^USER^&password=^PASS^"
            fail_string = "Invalid credentials"
            cmd.extend(['-s', str(port), target, 'http-post-form', f'{login_path}:{form_data}:{fail_string}'])
        elif service == 'http-basic':
            cmd.extend(['-s', str(port), target, 'http-basic'])
        elif service in ['ftp', 'ssh', 'telnet', 'smb']:
            cmd.extend(['-s', str(port), target, service])
        else:
            cmd.extend(['-s', str(port), target, service])

        if extra_params:
            cmd.extend(extra_params.split())

        print(f"Running command: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        if result.returncode == 0 or '1 valid password found' in result.stdout:
            print("Hydra brute force completed - found credentials!")
            # Parse results
            lines = result.stdout.split('\n')
            found_creds = [line for line in lines if '[http-post-form]' in line or '[login]' in line]
            return {
                "output": result.stdout,
                "found_credentials": found_creds,
                "success": True,
                "timestamp": time.time()
            }
        else:
            print("Hydra brute force completed - no credentials found.")
            return {
                "output": result.stdout,
                "found_credentials": [],
                "success": True,
                "timestamp": time.time()
            }

    except FileNotFoundError:
        print("Hydra not installed. Skipping brute force test.")
        return None
    except subprocess.TimeoutExpired:
        print("Hydra brute force timed out.")
        return {
            "error": "Timeout",
            "success": False,
            "timestamp": time.time()
        }
    except Exception as e:
        print(f"Error during Hydra brute force: {e}")
        return {
            "error": str(e),
            "success": False,
            "timestamp": time.time()
        }

def perform_hydra_http_brute_force(base_url, username_list=None, password_list=None):
    """
    Perform HTTP brute force specifically for web applications.

    Args:
        base_url (str): Target URL
        username_list (str): Path to username list
        password_list (str): Path to password list

    Returns:
        dict: Brute force results
    """
    # Extract host and port from URL
    from urllib.parse import urlparse
    parsed = urlparse(base_url)
    host = parsed.hostname
    port = parsed.port or (443 if parsed.scheme == 'https' else 80)

    # For HTTP forms, we need more specific parameters
    # This is a simplified version - in practice, would need form analysis
    return perform_hydra_brute_force(
        host, port,
        service='http-post-form',
        username=username_list,
        password_list=password_list,
        extra_params=f'-m /login:username=^USER^&password=^PASS^:F=invalid'
    )
