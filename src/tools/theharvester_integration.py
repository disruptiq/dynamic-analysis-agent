"""
TheHarvester OSINT integration for the Dynamic Analysis Agent.

TheHarvester is a tool for gathering e-mail accounts, user names and hostnames/subdomains
from different public sources like search engines, PGP key servers and SHODAN computer
database.

This integration performs comprehensive OSINT gathering including:
- Email address harvesting from search engines
- Subdomain enumeration from various sources
- Username collection from social media
- Hostname discovery and IP resolution
- LinkedIn profile discovery
- Twitter username enumeration
- Shodan integration for device discovery

Used for:
- Target reconnaissance and profiling
- Email harvesting for social engineering
- Subdomain discovery for attack surface mapping
- Intelligence gathering for security assessments
"""

import subprocess
import time
import json

def perform_theharvester_scan(domain, sources=None, limit=500):
    """
    Perform TheHarvester OSINT scan.

    Args:
        domain (str): Target domain
        sources (list): List of sources to query
        limit (int): Result limit per source

    Returns:
        dict: OSINT results
    """
    try:
        print(f"\nRunning TheHarvester on {domain}...")

        cmd = ['theHarvester', '-d', domain, '-l', str(limit), '-f', 'json']

        if sources:
            for source in sources:
                cmd.extend(['-b', source])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )

        if result.returncode == 0:
            print("TheHarvester scan completed.")

            # Parse JSON output if available
            json_file = f"{domain}.json"
            results = {
                "emails": [],
                "hosts": [],
                "urls": [],
                "users": [],
                "ips": []
            }

            try:
                if os.path.exists(json_file):
                    with open(json_file, 'r') as f:
                        data = json.load(f)

                    if 'emails' in data:
                        results['emails'] = data['emails']
                    if 'hosts' in data:
                        results['hosts'] = data['hosts']
                    if 'urls' in data:
                        results['urls'] = data['urls']
                    if 'linkedin_links' in data:
                        results['users'].extend(data['linkedin_links'])
                    if 'twitter_links' in data:
                        results['users'].extend(data['twitter_links'])

                    # Clean up
                    os.remove(json_file)

            except (json.JSONDecodeError, FileNotFoundError):
                # Fallback to parsing stdout
                lines = result.stdout.split('\n')
                for line in lines:
                    if '@' in line and domain in line:
                        results['emails'].append(line.strip())
                    elif 'Subdomain' in line or ':' in line:
                        results['hosts'].append(line.strip())

            return {
                "output": result.stdout,
                "domain": domain,
                "emails": results['emails'],
                "hosts": results['hosts'],
                "urls": results['urls'],
                "users": results['users'],
                "ips": results['ips'],
                "email_count": len(results['emails']),
                "host_count": len(results['hosts']),
                "url_count": len(results['urls']),
                "user_count": len(results['users']),
                "sources": sources or ['all'],
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
        print("TheHarvester not installed. Skipping OSINT gathering.")
        return None
    except subprocess.TimeoutExpired:
        print("TheHarvester timed out.")
        return {
            "error": "Timeout",
            "domain": domain,
            "success": False,
            "timestamp": time.time()
        }
    except Exception as e:
        print(f"Error during TheHarvester scan: {e}")
        return {
            "error": str(e),
            "domain": domain,
            "success": False,
            "timestamp": time.time()
        }

def perform_theharvester_email_harvest(domain, limit=100):
    """
    Harvest emails specifically for a domain.

    Args:
        domain (str): Target domain
        limit (int): Email limit

    Returns:
        dict: Email harvesting results
    """
    return perform_theharvester_scan(domain, sources=['google', 'bing', 'yahoo'], limit=limit)

def perform_theharvester_subdomain_enum(domain, limit=200):
    """
    Enumerate subdomains for a domain.

    Args:
        domain (str): Target domain
        limit (int): Subdomain limit

    Returns:
        dict: Subdomain enumeration results
    """
    return perform_theharvester_scan(domain, sources=['google', 'bing', 'yahoo', 'virustotal', 'threatcrowd'], limit=limit)
