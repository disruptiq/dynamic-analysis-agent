"""
Qsreplace query string replacement integration for the Dynamic Analysis Agent.
"""

import subprocess
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

def check_qsreplace_available() -> bool:
    """Check if Qsreplace is available on the system."""
    try:
        result = subprocess.run(['qsreplace', '--help'], capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def perform_qsreplace_replacement(urls: List[str], replacement: str, timeout: int = 60) -> Optional[Dict]:
    """
    Perform query string parameter replacement using Qsreplace.

    Args:
        urls (list): List of URLs to process
        replacement (str): String to replace parameter values with
        timeout (int): Timeout in seconds

    Returns:
        dict: Results with modified URLs
    """
    if not check_qsreplace_available():
        logger.warning("Qsreplace is not available on this system")
        return None

    try:
        # Write URLs to stdin
        url_input = '\n'.join(urls)

        cmd = ['qsreplace', replacement]

        logger.info(f"Running Qsreplace on {len(urls)} URLs with replacement: {replacement}")
        result = subprocess.run(cmd, input=url_input, capture_output=True, text=True, timeout=timeout)

        if result.returncode == 0:
            modified_urls = result.stdout.strip().split('\n')
            modified_urls = [u.strip() for u in modified_urls if u.strip()]

            return {
                'tool': 'qsreplace',
                'urls_processed': len(urls),
                'replacement': replacement,
                'modified_urls': modified_urls,
                'success': True
            }
        else:
            logger.error(f"Qsreplace failed: {result.stderr}")
            return {
                'tool': 'qsreplace',
                'urls_processed': len(urls),
                'replacement': replacement,
                'error': result.stderr,
                'success': False
            }

    except subprocess.TimeoutExpired:
        logger.error(f"Qsreplace timed out after {timeout} seconds")
        return {
            'tool': 'qsreplace',
            'urls_processed': len(urls),
            'replacement': replacement,
            'error': 'Timeout',
            'success': False
        }
    except Exception as e:
        logger.error(f"Error running Qsreplace: {e}")
        return {
            'tool': 'qsreplace',
            'urls_processed': len(urls),
            'replacement': replacement,
            'error': str(e),
            'success': False
        }

def perform_qsreplace_fuzz(urls: List[str], fuzz_strings: List[str], timeout: int = 60) -> Optional[Dict]:
    """
    Perform fuzzing with multiple replacements using Qsreplace.

    Args:
        urls (list): List of URLs to process
        fuzz_strings (list): List of strings to use for replacement
        timeout (int): Timeout in seconds

    Returns:
        dict: Results with all modified URLs
    """
    if not check_qsreplace_available():
        logger.warning("Qsreplace is not available on this system")
        return None

    all_results = []

    for fuzz_string in fuzz_strings:
        result = perform_qsreplace_replacement(urls, fuzz_string, timeout)
        if result and result['success']:
            all_results.extend(result['modified_urls'])

    return {
        'tool': 'qsreplace_fuzz',
        'urls_processed': len(urls),
        'fuzz_strings': len(fuzz_strings),
        'total_modified_urls': len(all_results),
        'modified_urls': all_results,
        'success': True
    }
