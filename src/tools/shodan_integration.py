"""
Shodan API integration for the Dynamic Analysis Agent.

Shodan is a search engine for Internet-connected devices. It provides information
about devices connected to the internet, including their geographical location,
software versions, and other metadata.

This integration performs internet-wide device discovery including:
- Device search by IP, hostname, or service
- Vulnerability correlation with Shodan data
- Port scanning results from Shodan
- Service banner information
- Geographical location data
- Historical scan data access

Used for:
- Internet-wide reconnaissance
- Vulnerability correlation
- Attack surface discovery
- Threat intelligence gathering
- Service enumeration across the internet
"""

import time
import os

def perform_shodan_search(query, api_key=None, limit=100):
    """
    Perform Shodan search using API.

    Args:
        query (str): Shodan search query
        api_key (str): Shodan API key
        limit (int): Result limit

    Returns:
        dict: Search results
    """
    try:
        print(f"\nSearching Shodan for: {query}")

        if not api_key:
            api_key = os.getenv('SHODAN_API_KEY')

        if not api_key:
            return {
                "error": "No Shodan API key provided. Set SHODAN_API_KEY environment variable.",
                "query": query,
                "success": False,
                "timestamp": time.time()
            }

        # Import shodan library
        import shodan

        api = shodan.Shodan(api_key)

        # Perform search
        results = api.search(query, limit=limit)

        # Extract relevant information
        devices = []
        for result in results['matches']:
            device = {
                'ip': result.get('ip_str'),
                'port': result.get('port'),
                'hostname': result.get('hostnames', []),
                'country': result.get('location', {}).get('country_name'),
                'city': result.get('location', {}).get('city'),
                'org': result.get('org'),
                'os': result.get('os'),
                'product': result.get('product'),
                'version': result.get('version'),
                'vulns': result.get('vulns', []),
                'data': result.get('data', ''),
                'timestamp': result.get('timestamp')
            }
            devices.append(device)

        return {
            "query": query,
            "total_results": results.get('total', 0),
            "devices": devices,
            "device_count": len(devices),
            "success": True,
            "timestamp": time.time()
        }

    except ImportError:
        print("Shodan Python library not installed. Install with: pip install shodan")
        return {
            "error": "Shodan library not installed",
            "query": query,
            "success": False,
            "timestamp": time.time()
        }
    except Exception as e:
        print(f"Error during Shodan search: {e}")
        return {
            "error": str(e),
            "query": query,
            "success": False,
            "timestamp": time.time()
        }

def perform_shodan_host_lookup(ip, api_key=None):
    """
    Look up specific host information on Shodan.

    Args:
        ip (str): IP address to look up
        api_key (str): Shodan API key

    Returns:
        dict: Host information
    """
    try:
        print(f"\nLooking up Shodan info for IP: {ip}")

        if not api_key:
            api_key = os.getenv('SHODAN_API_KEY')

        if not api_key:
            return {
                "error": "No Shodan API key provided",
                "ip": ip,
                "success": False,
                "timestamp": time.time()
            }

        import shodan
        api = shodan.Shodan(api_key)

        host = api.host(ip)

        device = {
            'ip': host.get('ip_str'),
            'hostnames': host.get('hostnames', []),
            'country': host.get('country_name'),
            'city': host.get('city'),
            'org': host.get('org'),
            'os': host.get('os'),
            'ports': host.get('ports', []),
            'services': []
        }

        # Extract service information
        for item in host.get('data', []):
            service = {
                'port': item.get('port'),
                'transport': item.get('transport'),
                'product': item.get('product'),
                'version': item.get('version'),
                'banner': item.get('data', ''),
                'vulns': item.get('vulns', [])
            }
            device['services'].append(service)

        return {
            "ip": ip,
            "device": device,
            "success": True,
            "timestamp": time.time()
        }

    except Exception as e:
        print(f"Error during Shodan host lookup: {e}")
        return {
            "error": str(e),
            "ip": ip,
            "success": False,
            "timestamp": time.time()
        }

def correlate_vulnerabilities(shodan_results, vuln_database):
    """
    Correlate Shodan findings with vulnerability database.

    Args:
        shodan_results (dict): Shodan search results
        vuln_database (dict): Vulnerability database

    Returns:
        dict: Correlated vulnerabilities
    """
    correlations = []

    for device in shodan_results.get('devices', []):
        device_vulns = device.get('vulns', [])
        product = device.get('product', '')
        version = device.get('version', '')

        # Check for known vulnerable software
        for vuln_id, vuln_info in vuln_database.items():
            if product.lower() in vuln_info.get('affected', '').lower():
                if not version or version in vuln_info.get('versions', []):
                    correlations.append({
                        'device_ip': device['ip'],
                        'vulnerability': vuln_id,
                        'severity': vuln_info.get('severity'),
                        'description': vuln_info.get('description'),
                        'product': product,
                        'version': version
                    })

    return {
        "correlations": correlations,
        "correlation_count": len(correlations),
        "timestamp": time.time()
    }
