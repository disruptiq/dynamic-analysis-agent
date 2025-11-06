"""
Httprobe HTTP probing integration for the Dynamic Analysis Agent.
"""

import subprocess
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

def check_httprobe_available() -> bool:
    """Check if Httprobe is available on the system."""
    try:
        result = subprocess.run(['httprobe', '--help'], capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def perform_httprobe_scan(domains: List[str], timeout: int = 300) -> Optional[Dict]:
    """
    Perform HTTP probing on a list of domains using Httprobe.

    Args:
        domains (list): List of domains/subdomains to probe
        timeout (int): Timeout in seconds

    Returns:
        dict: Scan results with HTTP endpoints found
    """
    if not check_httprobe_available():
        logger.warning("Httprobe is not available on this system")
        return None

    try:
        # Write domains to stdin
        domain_input = '\n'.join(domains)

        cmd = ['httprobe']

        logger.info(f"Running Httprobe scan on {len(domains)} domains")
        result = subprocess.run(cmd, input=domain_input, capture_output=True, text=True, timeout=timeout)

        if result.returncode == 0:
            endpoints = result.stdout.strip().split('\n')
            endpoints = [e.strip() for e in endpoints if e.strip()]

            return {
                'tool': 'httprobe',
                'domains_probed': len(domains),
                'endpoints_found': len(endpoints),
                'endpoints': endpoints,
                'success': True
            }
        else:
            logger.error(f"Httprobe scan failed: {result.stderr}")
            return {
                'tool': 'httprobe',
                'domains_probed': len(domains),
                'error': result.stderr,
                'success': False
            }

    except subprocess.TimeoutExpired:
        logger.error(f"Httprobe scan timed out after {timeout} seconds")
        return {
            'tool': 'httprobe',
            'domains_probed': len(domains),
            'error': 'Timeout',
            'success': False
        }
    except Exception as e:
        logger.error(f"Error running Httprobe: {e}")
        return {
            'tool': 'httprobe',
            'domains_probed': len(domains),
            'error': str(e),
            'success': False
        }

def perform_httprobe_prefer_https(domains: List[str], timeout: int = 300) -> Optional[Dict]:
    """
    Perform HTTP probing with HTTPS preference.

    Args:
        domains (list): List of domains/subdomains to probe
        timeout (int): Timeout in seconds

    Returns:
        dict: Scan results with HTTPS endpoints preferred
    """
    if not check_httprobe_available():
        logger.warning("Httprobe is not available on this system")
        return None

    try:
        domain_input = '\n'.join(domains)

        cmd = ['httprobe', '-p', 'https:443', '-p', 'http:80']

        logger.info(f"Running Httprobe (HTTPS prefer) scan on {len(domains)} domains")
        result = subprocess.run(cmd, input=domain_input, capture_output=True, text=True, timeout=timeout)

        if result.returncode == 0:
            endpoints = result.stdout.strip().split('\n')
            endpoints = [e.strip() for e in endpoints if e.strip()]

            return {
                'tool': 'httprobe_https_prefer',
                'domains_probed': len(domains),
                'endpoints_found': len(endpoints),
                'endpoints': endpoints,
                'success': True
            }
        else:
            logger.error(f"Httprobe HTTPS prefer scan failed: {result.stderr}")
            return {
                'tool': 'httprobe_https_prefer',
                'domains_probed': len(domains),
                'error': result.stderr,
                'success': False
            }

    except subprocess.TimeoutExpired:
        logger.error(f"Httprobe HTTPS prefer scan timed out after {timeout} seconds")
        return {
            'tool': 'httprobe_https_prefer',
            'domains_probed': len(domains),
            'error': 'Timeout',
            'success': False
        }
    except Exception as e:
        logger.error(f"Error running Httprobe HTTPS prefer: {e}")
        return {
            'tool': 'httprobe_https_prefer',
            'domains_probed': len(domains),
            'error': str(e),
            'success': False
        }
