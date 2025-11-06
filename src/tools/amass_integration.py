"""
Amass DNS/subdomain enumeration integration for the Dynamic Analysis Agent.
"""

import subprocess
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

def check_amass_available() -> bool:
    """Check if Amass is available on the system."""
    try:
        result = subprocess.run(['amass', '--version'], capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def perform_amass_scan(domain: str, passive: bool = True, timeout: int = 300) -> Optional[Dict]:
    """
    Perform DNS/subdomain enumeration using Amass.

    Args:
        domain (str): Target domain for enumeration
        passive (bool): Use passive enumeration only
        timeout (int): Timeout in seconds

    Returns:
        dict: Scan results with subdomains found
    """
    if not check_amass_available():
        logger.warning("Amass is not available on this system")
        return None

    try:
        cmd = ['amass', 'enum', '-d', domain]
        if passive:
            cmd.extend(['-passive'])

        logger.info(f"Running Amass scan on domain: {domain}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

        if result.returncode == 0:
            subdomains = result.stdout.strip().split('\n')
            subdomains = [s.strip() for s in subdomains if s.strip()]

            return {
                'tool': 'amass',
                'domain': domain,
                'passive': passive,
                'subdomains_found': len(subdomains),
                'subdomains': subdomains,
                'success': True
            }
        else:
            logger.error(f"Amass scan failed: {result.stderr}")
            return {
                'tool': 'amass',
                'domain': domain,
                'error': result.stderr,
                'success': False
            }

    except subprocess.TimeoutExpired:
        logger.error(f"Amass scan timed out after {timeout} seconds")
        return {
            'tool': 'amass',
            'domain': domain,
            'error': 'Timeout',
            'success': False
        }
    except Exception as e:
        logger.error(f"Error running Amass: {e}")
        return {
            'tool': 'amass',
            'domain': domain,
            'error': str(e),
            'success': False
        }

def perform_amass_intel(domain: str, timeout: int = 300) -> Optional[Dict]:
    """
    Perform intelligence gathering using Amass.

    Args:
        domain (str): Target domain
        timeout (int): Timeout in seconds

    Returns:
        dict: Intelligence results
    """
    if not check_amass_available():
        logger.warning("Amass is not available on this system")
        return None

    try:
        cmd = ['amass', 'intel', '-d', domain]

        logger.info(f"Running Amass intel on domain: {domain}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

        if result.returncode == 0:
            intel_data = result.stdout.strip()

            return {
                'tool': 'amass_intel',
                'domain': domain,
                'intel_data': intel_data,
                'success': True
            }
        else:
            logger.error(f"Amass intel failed: {result.stderr}")
            return {
                'tool': 'amass_intel',
                'domain': domain,
                'error': result.stderr,
                'success': False
            }

    except subprocess.TimeoutExpired:
        logger.error(f"Amass intel timed out after {timeout} seconds")
        return {
            'tool': 'amass_intel',
            'domain': domain,
            'error': 'Timeout',
            'success': False
        }
    except Exception as e:
        logger.error(f"Error running Amass intel: {e}")
        return {
            'tool': 'amass_intel',
            'domain': domain,
            'error': str(e),
            'success': False
        }
