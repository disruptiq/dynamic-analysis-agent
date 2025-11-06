"""
Dotdotpwn directory traversal integration for the Dynamic Analysis Agent.
"""

import subprocess
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

def check_dotdotpwn_available() -> bool:
    """Check if Dotdotpwn is available on the system."""
    try:
        result = subprocess.run(['dotdotpwn.pl', '--help'], capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def perform_dotdotpwn_scan(url: str, module: str = 'http', timeout: int = 300) -> Optional[Dict]:
    """
    Perform directory traversal testing using Dotdotpwn.

    Args:
        url (str): Target URL to test
        module (str): Module to use (http, ftp, etc.)
        timeout (int): Timeout in seconds

    Returns:
        dict: Scan results with traversal vulnerabilities found
    """
    if not check_dotdotpwn_available():
        logger.warning("Dotdotpwn is not available on this system")
        return None

    try:
        cmd = ['dotdotpwn.pl', '-m', module, '-h', url, '-q']  # -q for quiet mode

        logger.info(f"Running Dotdotpwn scan on URL: {url} with module: {module}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

        if result.returncode == 0:
            # Parse Dotdotpwn output for vulnerabilities
            output_lines = result.stdout.strip().split('\n')
            vulnerabilities = []

            for line in output_lines:
                line = line.strip()
                if 'Vulnerable' in line or 'Traversal' in line or 'Found' in line:
                    vulnerabilities.append(line)

            return {
                'tool': 'dotdotpwn',
                'url': url,
                'module': module,
                'vulnerabilities_found': len(vulnerabilities),
                'vulnerabilities': vulnerabilities,
                'success': True
            }
        else:
            logger.error(f"Dotdotpwn scan failed: {result.stderr}")
            return {
                'tool': 'dotdotpwn',
                'url': url,
                'module': module,
                'error': result.stderr,
                'success': False
            }

    except subprocess.TimeoutExpired:
        logger.error(f"Dotdotpwn scan timed out after {timeout} seconds")
        return {
            'tool': 'dotdotpwn',
            'url': url,
            'module': module,
            'error': 'Timeout',
            'success': False
        }
    except Exception as e:
        logger.error(f"Error running Dotdotpwn: {e}")
        return {
            'tool': 'dotdotpwn',
            'url': url,
            'module': module,
            'error': str(e),
            'success': False
        }

def perform_dotdotpwn_traversal_test(url: str, traversal_string: str, timeout: int = 300) -> Optional[Dict]:
    """
    Test specific directory traversal strings using Dotdotpwn.

    Args:
        url (str): Target URL to test
        traversal_string (str): Specific traversal string to test
        timeout (int): Timeout in seconds

    Returns:
        dict: Test results
    """
    if not check_dotdotpwn_available():
        logger.warning("Dotdotpwn is not available on this system")
        return None

    try:
        cmd = ['dotdotpwn.pl', '-m', 'http', '-h', url, '-s', traversal_string, '-q']

        logger.info(f"Running Dotdotpwn traversal test on URL: {url} with string: {traversal_string}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

        if result.returncode == 0:
            output_lines = result.stdout.strip().split('\n')
            results = []

            for line in output_lines:
                line = line.strip()
                if line:
                    results.append(line)

            return {
                'tool': 'dotdotpwn_traversal',
                'url': url,
                'traversal_string': traversal_string,
                'results': results,
                'success': True
            }
        else:
            logger.error(f"Dotdotpwn traversal test failed: {result.stderr}")
            return {
                'tool': 'dotdotpwn_traversal',
                'url': url,
                'traversal_string': traversal_string,
                'error': result.stderr,
                'success': False
            }

    except subprocess.TimeoutExpired:
        logger.error(f"Dotdotpwn traversal test timed out after {timeout} seconds")
        return {
            'tool': 'dotdotpwn_traversal',
            'url': url,
            'traversal_string': traversal_string,
            'error': 'Timeout',
            'success': False
        }
    except Exception as e:
        logger.error(f"Error running Dotdotpwn traversal test: {e}")
        return {
            'tool': 'dotdotpwn_traversal',
            'url': url,
            'traversal_string': traversal_string,
            'error': str(e),
            'success': False
        }
