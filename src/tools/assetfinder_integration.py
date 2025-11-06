"""
Assetfinder asset discovery integration for the Dynamic Analysis Agent.
"""

import subprocess
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

def check_assetfinder_available() -> bool:
    """Check if Assetfinder is available on the system."""
    try:
        result = subprocess.run(['assetfinder', '--help'], capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def perform_assetfinder_scan(domain: str, timeout: int = 300) -> Optional[Dict]:
    """
    Perform asset discovery using Assetfinder.

    Args:
        domain (str): Target domain for asset discovery
        timeout (int): Timeout in seconds

    Returns:
        dict: Scan results with assets found
    """
    if not check_assetfinder_available():
        logger.warning("Assetfinder is not available on this system")
        return None

    try:
        cmd = ['assetfinder', '--subs-only', domain]

        logger.info(f"Running Assetfinder scan on domain: {domain}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

        if result.returncode == 0:
            assets = result.stdout.strip().split('\n')
            assets = [a.strip() for a in assets if a.strip()]

            return {
                'tool': 'assetfinder',
                'domain': domain,
                'assets_found': len(assets),
                'assets': assets,
                'success': True
            }
        else:
            logger.error(f"Assetfinder scan failed: {result.stderr}")
            return {
                'tool': 'assetfinder',
                'domain': domain,
                'error': result.stderr,
                'success': False
            }

    except subprocess.TimeoutExpired:
        logger.error(f"Assetfinder scan timed out after {timeout} seconds")
        return {
            'tool': 'assetfinder',
            'domain': domain,
            'error': 'Timeout',
            'success': False
        }
    except Exception as e:
        logger.error(f"Error running Assetfinder: {e}")
        return {
            'tool': 'assetfinder',
            'domain': domain,
            'error': str(e),
            'success': False
        }

def perform_assetfinder_company(company: str, timeout: int = 300) -> Optional[Dict]:
    """
    Perform asset discovery for a company using Assetfinder.

    Args:
        company (str): Company name for asset discovery
        timeout (int): Timeout in seconds

    Returns:
        dict: Scan results with company assets found
    """
    if not check_assetfinder_available():
        logger.warning("Assetfinder is not available on this system")
        return None

    try:
        cmd = ['assetfinder', company]

        logger.info(f"Running Assetfinder scan for company: {company}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

        if result.returncode == 0:
            assets = result.stdout.strip().split('\n')
            assets = [a.strip() for a in assets if a.strip()]

            return {
                'tool': 'assetfinder_company',
                'company': company,
                'assets_found': len(assets),
                'assets': assets,
                'success': True
            }
        else:
            logger.error(f"Assetfinder company scan failed: {result.stderr}")
            return {
                'tool': 'assetfinder_company',
                'company': company,
                'error': result.stderr,
                'success': False
            }

    except subprocess.TimeoutExpired:
        logger.error(f"Assetfinder company scan timed out after {timeout} seconds")
        return {
            'tool': 'assetfinder_company',
            'company': company,
            'error': 'Timeout',
            'success': False
        }
    except Exception as e:
        logger.error(f"Error running Assetfinder for company: {e}")
        return {
            'tool': 'assetfinder_company',
            'company': company,
            'error': str(e),
            'success': False
        }
