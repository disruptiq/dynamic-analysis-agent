"""
Gf pattern matching integration for the Dynamic Analysis Agent.
"""

import subprocess
import logging
import os
import tempfile
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

def check_gf_available() -> bool:
    """Check if Gf is available on the system."""
    try:
        result = subprocess.run(['gf', '--help'], capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def perform_gf_scan(content: str, patterns: Optional[List[str]] = None, timeout: int = 60) -> Optional[Dict]:
    """
    Perform pattern matching on content using Gf.

    Args:
        content (str): Content to scan for patterns
        patterns (list): Specific Gf patterns to use (optional)
        timeout (int): Timeout in seconds

    Returns:
        dict: Scan results with pattern matches found
    """
    if not check_gf_available():
        logger.warning("Gf is not available on this system")
        return None

    try:
        # Write content to temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(content)
            temp_file = f.name

        results = {}

        if patterns:
            # Use specific patterns
            for pattern in patterns:
                cmd = ['gf', pattern, temp_file]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
                if result.returncode == 0:
                    matches = result.stdout.strip().split('\n') if result.stdout.strip() else []
                    results[pattern] = matches
                else:
                    logger.warning(f"Gf pattern {pattern} failed: {result.stderr}")
        else:
            # Use all available patterns
            cmd = ['gf', '--list']
            list_result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if list_result.returncode == 0:
                available_patterns = list_result.stdout.strip().split('\n')
                available_patterns = [p.strip() for p in available_patterns if p.strip()]

                for pattern in available_patterns[:10]:  # Limit to first 10 to avoid too many
                    cmd = ['gf', pattern, temp_file]
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
                    if result.returncode == 0:
                        matches = result.stdout.strip().split('\n') if result.stdout.strip() else []
                        if matches:
                            results[pattern] = matches

        # Clean up temp file
        os.unlink(temp_file)

        return {
            'tool': 'gf',
            'patterns_scanned': len(results),
            'matches_found': sum(len(matches) for matches in results.values()),
            'results': results,
            'success': True
        }

    except subprocess.TimeoutExpired:
        logger.error(f"Gf scan timed out after {timeout} seconds")
        return {
            'tool': 'gf',
            'error': 'Timeout',
            'success': False
        }
    except Exception as e:
        logger.error(f"Error running Gf: {e}")
        return {
            'tool': 'gf',
            'error': str(e),
            'success': False
        }

def get_gf_patterns() -> List[str]:
    """
    Get available Gf patterns.

    Returns:
        list: List of available patterns
    """
    if not check_gf_available():
        return []

    try:
        result = subprocess.run(['gf', '--list'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            patterns = result.stdout.strip().split('\n')
            return [p.strip() for p in patterns if p.strip()]
        return []
    except Exception:
        return []
