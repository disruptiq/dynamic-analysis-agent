"""
Rapid7 Nexpose integration for the Dynamic Analysis Agent.

Rapid7 Nexpose is a vulnerability scanner that aims to support the entire
vulnerability management lifecycle, including discovery, detection, verification,
risk classification, impact analysis, reporting, and mitigation.

This integration performs enterprise vulnerability management including:
- Live network scanning
- Vulnerability detection and assessment
- Risk scoring and prioritization
- Policy compliance checking
- Remediation tracking

Scans for:
- Network-based vulnerabilities
- System configuration issues
- Application security flaws
- Policy compliance gaps
- Risk-ranked security issues
"""

import requests
import time
import json

class Rapid7NexposeIntegration:
    def __init__(self, host='localhost', port=3780, username=None, password=None):
        """
        Initialize Rapid7 Nexpose integration.

        Args:
            host (str): Nexpose server host
            port (int): Nexpose server port
            username (str): Username
            password (str): Password
        """
        self.base_url = f"https://{host}:{port}/api/3"
        self.session = requests.Session()
        self.session.verify = False

        if username and password:
            self.authenticate(username, password)

    def authenticate(self, username, password):
        """Authenticate with Nexpose."""
        try:
            response = self.session.post(f"{self.base_url}/authentication/login", json={
                "username": username,
                "password": password
            })
            if response.status_code == 200:
                token = response.json().get('token')
                self.session.headers.update({'Authorization': f'Bearer {token}'})
                print("Rapid7 Nexpose authentication successful")
            else:
                print(f"Rapid7 Nexpose authentication failed: {response.text}")
        except Exception as e:
            print(f"Error authenticating with Rapid7 Nexpose: {e}")

    def create_site(self, name, hosts):
        """
        Create a site.

        Args:
            name (str): Site name
            hosts (list): List of hosts

        Returns:
            dict: Site creation result
        """
        try:
            site_data = {
                "name": name,
                "hosts": hosts,
                "scanTemplateId": "full-audit"
            }

            response = self.session.post(f"{self.base_url}/sites", json=site_data)
            if response.status_code == 201:
                return {"site": response.json(), "success": True}
            else:
                return {"error": response.text, "success": False}
        except Exception as e:
            return {"error": str(e), "success": False}

    def start_scan(self, site_id):
        """
        Start a scan.

        Args:
            site_id (str): Site ID

        Returns:
            dict: Scan start result
        """
        try:
            response = self.session.post(f"{self.base_url}/sites/{site_id}/scans")
            if response.status_code == 201:
                return {"scan": response.json(), "success": True}
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
        try:
            response = self.session.get(f"{self.base_url}/scans/{scan_id}")
            if response.status_code == 200:
                return {"status": response.json(), "success": True}
            else:
                return {"error": response.text, "success": False}
        except Exception as e:
            return {"error": str(e), "success": False}

def perform_rapid7_nexpose_scan(targets, host='localhost', port=3780, username=None, password=None):
    """
    Perform Rapid7 Nexpose vulnerability scan.

    Args:
        targets (list): Target hosts
        host (str): Nexpose server host
        port (int): Nexpose server port
        username (str): Username
        password (str): Password

    Returns:
        dict: Scan results
    """
    try:
        nexpose = Rapid7NexposeIntegration(host, port, username, password)
        create_result = nexpose.create_site("DynamicAnalysisSite", targets)

        if not create_result["success"]:
            return create_result

        site_id = create_result["site"]["id"]

        start_result = nexpose.start_scan(site_id)
        if not start_result["success"]:
            return start_result

        scan_id = start_result["scan"]["id"]

        # Wait for completion
        print("Waiting for Rapid7 Nexpose scan to complete...")
        while True:
            status = nexpose.get_scan_status(scan_id)
            if status["success"]:
                scan_status = status["status"]["status"]
                if scan_status == "finished":
                    break
                print(".", end="", flush=True)
                time.sleep(30)
            else:
                return status

        print("Rapid7 Nexpose scan completed.")
        return {"message": "Scan completed", "scan_id": scan_id, "success": True, "timestamp": time.time()}

    except Exception as e:
        print(f"Error during Rapid7 Nexpose scan: {e}")
        return {"error": str(e), "success": False, "timestamp": time.time()}
