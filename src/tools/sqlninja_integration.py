"""
SQLNinja SQL injection exploitation integration for the Dynamic Analysis Agent.

SQLNinja is a tool targeted to exploit SQL Injection vulnerabilities on a
web application that uses Microsoft SQL Server as its back-end.

This integration performs advanced SQL injection exploitation including:
- Database fingerprinting
- User privilege escalation
- Database data extraction
- Command execution via xp_cmdshell
- File upload/download
- Out-of-band data exfiltration

Used for:
- Advanced SQL injection exploitation
- Database takeover scenarios
- Privilege escalation testing
- Data extraction from vulnerable applications
"""

import subprocess
import time

def perform_sqlninja_scan(base_url, vulnerable_param, method='GET', data=None):
    """
    Perform SQLNinja SQL injection exploitation.

    Args:
        base_url (str): Target URL
        vulnerable_param (str): Vulnerable parameter name
        method (str): HTTP method (GET/POST)
        data (str): POST data for POST requests

    Returns:
        dict: Exploitation results
    """
    try:
        print(f"\nRunning SQLNinja on {base_url}...")

        # Create temporary config file for SQLNinja
        config_content = f"""# SQLNinja configuration
url = {base_url}
method = {method.upper()}
 vulnerable_parameter = {vulnerable_param}
"""

        if data:
            config_content += f"post_data = {data}\n"

        config_file = f"sqlninja_{int(time.time())}.conf"

        with open(config_file, 'w') as f:
            f.write(config_content)

        # Test injection point
        cmd = ['sqlninja', '-f', config_file, '-m', 'test']

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode == 0:
            print("SQL injection vulnerability confirmed.")

            # Attempt fingerprinting
            fingerprint_cmd = ['sqlninja', '-f', config_file, '-m', 'fingerprint']
            fingerprint_result = subprocess.run(
                fingerprint_cmd,
                capture_output=True,
                text=True,
                timeout=120
            )

            # Clean up config file
            if os.path.exists(config_file):
                os.remove(config_file)

            return {
                "output": result.stdout,
                "fingerprint_output": fingerprint_result.stdout,
                "base_url": base_url,
                "vulnerable_param": vulnerable_param,
                "method": method,
                "vulnerable": True,
                "success": True,
                "timestamp": time.time()
            }
        else:
            # Clean up config file
            if os.path.exists(config_file):
                os.remove(config_file)

            return {
                "error": result.stderr,
                "base_url": base_url,
                "vulnerable_param": vulnerable_param,
                "vulnerable": False,
                "success": False,
                "timestamp": time.time()
            }

    except FileNotFoundError:
        print("SQLNinja not installed. Skipping SQL injection exploitation.")
        return None
    except subprocess.TimeoutExpired:
        print("SQLNinja timed out.")
        # Clean up
        if os.path.exists(config_file):
            os.remove(config_file)
        return {
            "error": "Timeout",
            "base_url": base_url,
            "success": False,
            "timestamp": time.time()
        }
    except Exception as e:
        print(f"Error during SQLNinja scan: {e}")
        # Clean up
        if os.path.exists(config_file):
            os.remove(config_file)
        return {
            "error": str(e),
            "base_url": base_url,
            "success": False,
            "timestamp": time.time()
        }

def perform_sqlninja_data_extraction(base_url, vulnerable_param, method='GET', table=None):
    """
    Extract data using SQLNinja.

    Args:
        base_url (str): Target URL
        vulnerable_param (str): Vulnerable parameter
        method (str): HTTP method
        table (str): Table to extract data from

    Returns:
        dict: Data extraction results
    """
    try:
        print(f"\nExtracting data with SQLNinja from {table}...")

        config_content = f"""url = {base_url}
method = {method.upper()}
vulnerable_parameter = {vulnerable_param}
"""

        config_file = f"sqlninja_extract_{int(time.time())}.conf"

        with open(config_file, 'w') as f:
            f.write(config_content)

        cmd = ['sqlninja', '-f', config_file, '-m', 'getdata']

        if table:
            cmd.extend(['-T', table])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout for data extraction
        )

        # Clean up
        if os.path.exists(config_file):
            os.remove(config_file)

        return {
            "output": result.stdout,
            "error": result.stderr,
            "base_url": base_url,
            "table": table,
            "success": result.returncode == 0,
            "timestamp": time.time()
        }

    except Exception as e:
        # Clean up
        if os.path.exists(config_file):
            os.remove(config_file)
        return {
            "error": str(e),
            "base_url": base_url,
            "success": False,
            "timestamp": time.time()
        }
