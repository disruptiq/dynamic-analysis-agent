"""
Ferret file disclosure integration for the Dynamic Analysis Agent.
"""

import subprocess
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

def check_ferret_available() -> bool:
    """Check if Ferret is available on the system."""
    try:
        result = subprocess.run(['ferret', '--help'], capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def perform_ferret_scan(url: str, timeout: int = 300) -> Optional[Dict]:
    """
    Perform file disclosure scanning using Ferret.

    Args:
        url (str): Target URL to scan
        timeout (int): Timeout in seconds

    Returns:
        dict: Scan results with potential file disclosures
    """
    if not check_ferret_available():
        logger.warning("Ferret is not available on this system")
        return None

    try:
        cmd = ['ferret', '-u', url]

        logger.info(f"Running Ferret scan on URL: {url}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

        if result.returncode == 0:
            # Parse Ferret output
            output_lines = result.stdout.strip().split('\n')
            disclosures = []

            for line in output_lines:
                line = line.strip()
                if line and ('[FOUND]' in line or 'File found' in line.lower()):
                    disclosures.append(line)

            return {
                'tool': 'ferret',
                'url': url,
                'disclosures_found': len(disclosures),
                'disclosures': disclosures,
                'success': True
            }
        else:
            logger.error(f"Ferret scan failed: {result.stderr}")
            return {
                'tool': 'ferret',
                'url': url,
                'error': result.stderr,
                'success': False
            }

    except subprocess.TimeoutExpired:
        logger.error(f"Ferret scan timed out after {timeout} seconds")
        return {
            'tool': 'ferret',
            'url': url,
            'error': 'Timeout',
            'success': False
        }
    except Exception as e:
        logger.error(f"Error running Ferret: {e}")
        return {
            'tool': 'ferret',
            'url': url,
            'error': str(e),
            'success': False
        }

def perform_ferret_wordlist_scan(url: str, wordlist: str, timeout: int = 300) -> Optional[Dict]:
    """
    Perform file disclosure scanning with custom wordlist using Ferret.

    Args:
        url (str): Target URL to scan
        wordlist (str): Path to wordlist file
        timeout (int): Timeout in seconds

    Returns:
        dict: Scan results with potential file disclosures
    """
    if not check_ferret_available():
        logger.warning("Ferret is not available on this system")
        return None

    try:
        cmd = ['ferret', '-u', url, '-w', wordlist]

        logger.info(f"Running Ferret wordlist scan on URL: {url} with wordlist: {wordlist}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

        if result.returncode == 0:
            output_lines = result.stdout.strip().split('\n')
            disclosures = []

            for line in output_lines:
                line = line.strip()
                if line and ('[FOUND]' in line or 'File found' in line.lower()):
                    disclosures.append(line)

            return {
                'tool': 'ferret_wordlist',
                'url': url,
                'wordlist': wordlist,
                'disclosures_found': len(disclosures),
                'disclosures': disclosures,
                'success': True
            }
        else:
            logger.error(f"Ferret wordlist scan failed: {result.stderr}")
            return {
                'tool': 'ferret_wordlist',
                'url': url,
                'wordlist': wordlist,
                'error': result.stderr,
                'success': False
            }

    except subprocess.TimeoutExpired:
        logger.error(f"Ferret wordlist scan timed out after {timeout} seconds")
        return {
            'tool': 'ferret_wordlist',
            'url': url,
            'wordlist': wordlist,
            'error': 'Timeout',
            'success': False
        }
    except Exception as e:
        logger.error(f"Error running Ferret wordlist: {e}")
        return {
            'tool': 'ferret_wordlist',
            'url': url,
            'wordlist': wordlist,
            'error': str(e),
            'success': False
        }
