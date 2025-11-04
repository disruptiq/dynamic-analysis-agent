"""
Nessus vulnerability scanner integration for the Dynamic Analysis Agent.

Nessus is a proprietary vulnerability scanner developed by Tenable, Inc.
It is one of the most popular vulnerability scanners, used to identify
vulnerabilities, configuration issues, and malware.

This integration performs comprehensive vulnerability scanning including:
- Network vulnerability assessment
- Configuration auditing
- Malware detection
- Compliance checking
- Patch management verification

Scans for:
- Known software vulnerabilities
- System misconfigurations
- Missing security patches
- Malware infections
- Compliance violations
"""

import requests
import time
import json

class NessusIntegration:
    def __init__(self, host='localhost', port=8834, username=None, password=None, api_key=None):
        """
        Initialize Nessus integration.

        Args:
            host (str): Nessus server host
            port (int): Nessus server port
            username (str): Nessus username
            password (str): Nessus password
            api_key (str): Nessus API key
        """
        self.host = host
        self.port = port
        self.base_url = f"https://{host}:{port}"
        self.session = requests.Session()
        self.session.verify = False  # Disable SSL verification for self-signed certs
        self.token = None

        if api_key:
            self.api_key = api_key
        elif username and password:
            self.authenticate(username, password)
        else:
            print("Nessus: No authentication provided")

    def authenticate(self, username, password):
        """Authenticate with Nessus server."""
        try:
            response = self.session.post(f"{self.base_url}/session", json={
                "username": username,
                "password": password
            })
            if response.status_code == 200:
                self.token = response.json().get('token')
                self.session.headers.update({'X-Cookie': f'token={self.token}'})
                print("Nessus authentication successful")
            else:
                print(f"Nessus authentication failed: {response.text}")
        except Exception as e:
            print(f"Error authenticating with Nessus: {e}")

    def create_scan(self, name, targets, policy_id=None):
        """
        Create a new scan.

        Args:
            name (str): Scan name
            targets (str): Target hosts/IPs
            policy_id (str): Policy ID to use

        Returns:
            dict: Scan creation result
        """
        if not self.token:
            return {"error": "Not authenticated", "success": False}

        try:
            scan_config = {
                "uuid": policy_id or "731a8e52-3ea6-a291-ec0a-d2ff0619c19d7bd788d6be818b65",  # Basic Network Scan
                "settings": {
                    "name": name,
                    "text_targets": targets
                }
            }

            response = self.session.post(f"{self.base_url}/scans", json=scan_config)
            if response.status_code == 200:
                return {"scan": response.json(), "success": True}
            else:
                return {"error": response.text, "success": False}
        except Exception as e:
            return {"error": str(e), "success": False}

    def launch_scan(self, scan_id):
        """
        Launch a scan.

        Args:
            scan_id (str): Scan ID to launch

        Returns:
            dict: Launch result
        """
        if not self.token:
            return {"error": "Not authenticated", "success": False}

        try:
            response = self.session.post(f"{self.base_url}/scans/{scan_id}/launch")
            if response.status_code == 200:
                return {"success": True}
            else:
                return {"error": response.text, "success": False}
        except Exception as e:
            return {"error": str(e), "success": False}

    def get_scan_status(self, scan_id):
        """
        Get scan status.

        Args:
            scan_id (str): Scan ID

        Returns:
            dict: Status information
        """
        if not self.token:
            return {"error": "Not authenticated", "success": False}

        try:
            response = self.session.get(f"{self.base_url}/scans/{scan_id}")
            if response.status_code == 200:
                return {"status": response.json(), "success": True}
            else:
                return {"error": response.text, "success": False}
        except Exception as e:
            return {"error": str(e), "success": False}

    def get_scan_results(self, scan_id):
        """
        Get scan results.

        Args:
            scan_id (str): Scan ID

        Returns:
            dict: Scan results
        """
        if not self.token:
            return {"error": "Not authenticated", "success": False}

        try:
            response = self.session.get(f"{self.base_url}/scans/{scan_id}")
            if response.status_code == 200:
                scan_data = response.json()
                return {"results": scan_data, "success": True}
            else:
                return {"error": response.text, "success": False}
        except Exception as e:
            return {"error": str(e), "success": False}

def perform_nessus_scan(targets, name="Dynamic Analysis Scan", host='localhost', port=8834, username=None, password=None):
    """
    Perform Nessus vulnerability scan.

    Args:
        targets (str): Target hosts/IPs
        name (str): Scan name
        host (str): Nessus server host
        port (int): Nessus server port
        username (str): Nessus username
        password (str): Nessus password

    Returns:
        dict: Scan results
    """
    try:
        nessus = NessusIntegration(host, port, username, password)
        if not nessus.token:
            return {"error": "Authentication failed", "success": False}

        # Create scan
        create_result = nessus.create_scan(name, targets)
        if not create_result["success"]:
            return create_result

        scan_id = create_result["scan"]["scan"]["id"]

        # Launch scan
        launch_result = nessus.launch_scan(scan_id)
        if not launch_result["success"]:
            return launch_result

        # Wait for completion
        print("Waiting for Nessus scan to complete...")
        while True:
            status = nessus.get_scan_status(scan_id)
            if status["success"]:
                scan_status = status["status"]["info"]["status"]
                if scan_status == "completed":
                    break
                elif scan_status == "running":
                    print(".", end="", flush=True)
                    time.sleep(30)
                else:
                    return {"error": f"Scan failed with status: {scan_status}", "success": False}
            else:
                return status
            time.sleep(10)

        # Get results
        results = nessus.get_scan_results(scan_id)
        print("Nessus scan completed.")
        return results

    except Exception as e:
        print(f"Error during Nessus scan: {e}")
        return {"error": str(e), "success": False, "timestamp": time.time()}
