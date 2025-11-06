"""
Sublist3r subdomain enumeration integration for the Dynamic Analysis Agent.
"""

import subprocess
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

def check_sublist3r_available() -> bool:
    """Check if Sublist3r is available on the system."""
    try:
        result = subprocess.run(['sublist3r', '--help'], capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def perform_sublist3r_scan(domain: str, engines: Optional[List[str]] = None, timeout: int = 300) -> Optional[Dict]:
    """
    Perform subdomain enumeration using Sublist3r.

    Args:
        domain (str): Target domain for enumeration
        engines (list): Specific search engines to use
        timeout (int): Timeout in seconds

    Returns:
        dict: Scan results with subdomains found
    """
    if not check_sublist3r_available():
        logger.warning("Sublist3r is not available on this system")
        return None

    try:
        cmd = ['sublist3r', '-d', domain, '-o', '/dev/null']  # Use /dev/null to avoid file output

        if engines:
            cmd.extend(['-e', ','.join(engines)])

        logger.info(f"Running Sublist3r scan on domain: {domain}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

        if result.returncode == 0:
            # Sublist3r outputs to stdout, parse the subdomains
            lines = result.stdout.strip().split('\n')
            subdomains = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('[') and 'Total Unique Subdomains Found' not in line:
                    if '.' in line and domain in line:
                        subdomains.append(line)

            return {
                'tool': 'sublist3r',
                'domain': domain,
                'engines': engines,
                'subdomains_found': len(subdomains),
                'subdomains': subdomains,
                'success': True
            }
        else:
            logger.error(f"Sublist3r scan failed: {result.stderr}")
            return {
                'tool': 'sublist3r',
                'domain': domain,
                'error': result.stderr,
                'success': False
            }

    except subprocess.TimeoutExpired:
        logger.error(f"Sublist3r scan timed out after {timeout} seconds")
        return {
            'tool': 'sublist3r',
            'domain': domain,
            'error': 'Timeout',
            'success': False
        }
    except Exception as e:
        logger.error(f"Error running Sublist3r: {e}")
        return {
            'tool': 'sublist3r',
            'domain': domain,
            'error': str(e),
            'success': False
        }

def get_sublist3r_engines() -> List[str]:
    """
    Get available search engines for Sublist3r.

    Returns:
        list: List of available engines
    """
    if not check_sublist3r_available():
        return []

    try:
        result = subprocess.run(['sublist3r', '--help'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            help_text = result.stdout
            # Parse engines from help text (this is approximate)
            engines = ['google', 'yahoo', 'bing', 'baidu', 'ask', 'netcraft', 'dnsdumpster', 'virustotal', 'threatcrowd', 'passivedns']
            return engines
        return []
    except Exception:
        return []
