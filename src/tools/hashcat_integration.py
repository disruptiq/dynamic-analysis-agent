"""
Hashcat GPU-accelerated password cracking integration for the Dynamic Analysis Agent.

Hashcat is the world's fastest and most advanced password recovery utility,
supporting five unique modes of attack for over 300 highly-optimized hashing algorithms.

This integration performs high-performance password cracking including:
- GPU acceleration for massive speed improvements
- Dictionary attacks
- Brute force attacks
- Hybrid attacks
- Mask attacks
- Rule-based attacks
- Support for all major hash types

Used for:
- High-performance password hash cracking
- GPU-accelerated security testing
- Advanced password recovery scenarios
"""

import subprocess
import time

def perform_hashcat_crack(hash_file, hash_type=None, wordlist=None, attack_mode=0, mask=None):
    """
    Perform GPU-accelerated password cracking with Hashcat.

    Args:
        hash_file (str): Path to file containing hashes
        hash_type (int): Hashcat hash type number
        wordlist (str): Path to wordlist file
        attack_mode (int): Attack mode (0=dict, 3=brute, 6=hybrid, 7=mask)
        mask (str): Mask pattern for brute force/mask attacks

    Returns:
        dict: Cracking results
    """
    try:
        print(f"\nRunning Hashcat on {hash_file}...")

        # Build command
        cmd = ['hashcat', '-m', str(hash_type)] if hash_type else ['hashcat']

        # Attack mode
        cmd.extend(['-a', str(attack_mode)])

        if attack_mode == 0 and wordlist:  # Dictionary attack
            cmd.append(wordlist)
        elif attack_mode == 3 and mask:  # Brute force with mask
            cmd.append(mask)
        elif attack_mode == 6 and wordlist and mask:  # Hybrid
            cmd.extend([wordlist, mask])
        elif attack_mode == 7 and mask:  # Mask attack
            cmd.append(mask)

        cmd.append(hash_file)

        # Add output options
        cmd.extend(['--status', '--status-timer', '10'])

        print(f"Running command: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=7200  # 2 hour timeout for GPU cracking
        )

        # Check for cracked passwords
        potfile = hash_file + '.potfile'
        cracked_count = 0
        cracked_passwords = []

        if os.path.exists(potfile):
            with open(potfile, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if ':' in line:
                        cracked_passwords.append(line.strip())
                        cracked_count += 1

        print(f"Hashcat completed - cracked {cracked_count} passwords.")

        return {
            "output": result.stdout,
            "cracked_passwords": cracked_passwords,
            "cracked_count": cracked_count,
            "hash_file": hash_file,
            "hash_type": hash_type,
            "attack_mode": attack_mode,
            "wordlist": wordlist,
            "mask": mask,
            "success": True,
            "timestamp": time.time()
        }

    except FileNotFoundError:
        print("Hashcat not installed. Skipping GPU cracking.")
        return None
    except subprocess.TimeoutExpired:
        print("Hashcat timed out.")
        return {
            "error": "Timeout",
            "hash_file": hash_file,
            "cracked_count": 0,
            "success": False,
            "timestamp": time.time()
        }
    except Exception as e:
        print(f"Error during Hashcat cracking: {e}")
        return {
            "error": str(e),
            "hash_file": hash_file,
            "success": False,
            "timestamp": time.time()
        }

def perform_hashcat_benchmark():
    """
    Run Hashcat benchmark to test GPU performance.

    Returns:
        dict: Benchmark results
    """
    try:
        print("\nRunning Hashcat benchmark...")

        result = subprocess.run(
            ['hashcat', '-b'],
            capture_output=True,
            text=True,
            timeout=300
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

def get_hashcat_hash_types():
    """
    Get list of supported hash types from Hashcat.

    Returns:
        list: List of hash types with numbers and descriptions
    """
    try:
        result = subprocess.run(
            ['hashcat', '--help'],
            capture_output=True,
            text=True
        )

        hash_types = []
        in_hash_section = False

        for line in result.stdout.split('\n'):
            if '-m, --hash-type=' in line:
                in_hash_section = True
                continue
            elif in_hash_section and line.strip().startswith('- '):
                break
            elif in_hash_section and line.strip():
                parts = line.strip().split(' | ', 1)
                if len(parts) == 2:
                    hash_types.append({
                        'number': parts[0].strip(),
                        'description': parts[1].strip()
                    })

        return hash_types

    except Exception:
        return []
