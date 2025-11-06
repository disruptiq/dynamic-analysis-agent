"""
John the Ripper password cracking integration for the Dynamic Analysis Agent.

John the Ripper is a fast password cracker, currently available for many
flavors of Unix, macOS, Windows, DOS, BeOS, and OpenVMS.

This integration performs offline password cracking including:
- Hash type auto-detection
- Dictionary attacks
- Brute force attacks
- Hybrid attacks (dictionary + rules)
- Support for hundreds of hash types
- GPU acceleration support

Used for:
- Cracking captured password hashes
- Testing password strength
- Security assessment of stored credentials
"""

import subprocess
import time
import os

def perform_john_crack(hash_file, wordlist=None, format=None, rules=None):
    """
    Perform password cracking with John the Ripper.

    Args:
        hash_file (str): Path to file containing hashes
        wordlist (str): Path to wordlist file
        format (str): Hash format (auto-detected if None)
        rules (str): John rules to apply

    Returns:
        dict: Cracking results
    """
    try:
        print(f"\nRunning John the Ripper on {hash_file}...")

        # Build command
        cmd = ['john']

        if format:
            cmd.extend(['--format', format])

        if wordlist:
            cmd.extend(['--wordlist', wordlist])

        if rules:
            cmd.extend(['--rules', rules])

        cmd.append(hash_file)

        print(f"Running command: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout for cracking
        )

        # Check for cracked passwords
        show_cmd = ['john', '--show', hash_file]
        show_result = subprocess.run(
            show_cmd,
            capture_output=True,
            text=True
        )

        cracked_count = 0
        cracked_passwords = []

        if show_result.returncode == 0:
            lines = show_result.stdout.strip().split('\n')
            for line in lines:
                if ':' in line and line.count(':') >= 1:
                    parts = line.split(':', 1)
                    if len(parts) == 2 and parts[1]:
                        cracked_passwords.append(line)
                        cracked_count += 1

        print(f"John the Ripper completed - cracked {cracked_count} passwords.")

        return {
            "output": result.stdout + "\n" + show_result.stdout,
            "cracked_passwords": cracked_passwords,
            "cracked_count": cracked_count,
            "hash_file": hash_file,
            "format": format,
            "wordlist": wordlist,
            "success": True,
            "timestamp": time.time()
        }

    except FileNotFoundError:
        print("John the Ripper not installed. Skipping password cracking.")
        return None
    except subprocess.TimeoutExpired:
        print("John the Ripper timed out.")
        return {
            "error": "Timeout",
            "hash_file": hash_file,
            "cracked_count": 0,
            "success": False,
            "timestamp": time.time()
        }
    except Exception as e:
        print(f"Error during John cracking: {e}")
        return {
            "error": str(e),
            "hash_file": hash_file,
            "success": False,
            "timestamp": time.time()
        }

def perform_john_benchmark():
    """
    Run John the Ripper benchmark to test performance.

    Returns:
        dict: Benchmark results
    """
    try:
        print("\nRunning John the Ripper benchmark...")

        result = subprocess.run(
            ['john', '--test'],
            capture_output=True,
            text=True,
            timeout=60
        )

        return {
            "output": result.stdout,
            "success": result.returncode == 0,
            "timestamp": time.time()
        }

    except Exception as e:
        return {
            "error": str(e),
            "success": False,
            "timestamp": time.time()
        }
