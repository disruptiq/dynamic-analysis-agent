"""
Tplmap template injection integration for the Dynamic Analysis Agent.

Tplmap is a tool that can be used to test for server-side template injection
vulnerabilities and exploit them by leveraging template engines to execute
arbitrary code on the server.

This integration performs template injection testing including:
- Multiple template engine support (Jinja2, Twig, Freemarker, etc.)
- Server-side template injection detection
- Code execution via template injection
- File system access through templates
- Information disclosure via template errors

Used for:
- Server-side template injection testing
- Template engine vulnerability assessment
- Code execution through SSTI
- Template-based information disclosure
"""

import subprocess
import time

def perform_tplmap_scan(base_url, vulnerable_param=None, method='GET', data=None, engine=None):
    """
    Perform Tplmap template injection scan.

    Args:
        base_url (str): Target URL
        vulnerable_param (str): Vulnerable parameter
        method (str): HTTP method
        data (str): POST data
        engine (str): Specific template engine to test

    Returns:
        dict: Scan results
    """
    try:
        print(f"\nRunning Tplmap on {base_url}...")

        cmd = ['tplmap']

        if method.upper() == 'POST' and data:
            cmd.extend(['-u', base_url, '-d', data])
        else:
            cmd.extend(['-u', base_url])

        if vulnerable_param:
            cmd.extend(['-p', vulnerable_param])

        if engine:
            cmd.extend(['-e', engine])

        # Add options for comprehensive testing
        cmd.extend(['--level', '5', '--os-shell'])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )

        if result.returncode == 0:
            print("Tplmap scan completed.")

            # Parse output for template engines and vulnerabilities
            lines = result.stdout.split('\n')
            template_engines = []
            injection_points = []
            code_execution = False

            for line in lines:
                if 'Template engine' in line:
                    template_engines.append(line.strip())
                if 'Parameter' in line and 'vulnerable' in line.lower():
                    injection_points.append(line.strip())
                if 'OS shell' in line or 'code execution' in line.lower():
                    code_execution = True

            return {
                "output": result.stdout,
                "base_url": base_url,
                "vulnerable_param": vulnerable_param,
                "method": method,
                "template_engines": template_engines,
                "injection_points": injection_points,
                "code_execution_possible": code_execution,
                "vulnerable": len(injection_points) > 0,
                "success": True,
                "timestamp": time.time()
            }
        else:
            return {
                "error": result.stderr,
                "base_url": base_url,
                "vulnerable_param": vulnerable_param,
                "vulnerable": False,
                "success": False,
                "timestamp": time.time()
            }

    except FileNotFoundError:
        print("Tplmap not installed. Skipping template injection testing.")
        return None
    except subprocess.TimeoutExpired:
        print("Tplmap timed out.")
        return {
            "error": "Timeout",
            "base_url": base_url,
            "success": False,
            "timestamp": time.time()
        }
    except Exception as e:
        print(f"Error during Tplmap scan: {e}")
        return {
            "error": str(e),
            "base_url": base_url,
            "success": False,
            "timestamp": time.time()
        }

def perform_tplmap_exploit(base_url, vulnerable_param, template_payload, engine=None):
    """
    Exploit template injection vulnerability.

    Args:
        base_url (str): Target URL
        vulnerable_param (str): Vulnerable parameter
        template_payload (str): Template injection payload
        engine (str): Template engine

    Returns:
        dict: Exploitation results
    """
    try:
        print(f"\nExploiting template injection with payload: {template_payload}")

        cmd = ['tplmap', '-u', base_url, '-p', vulnerable_param]

        if engine:
            cmd.extend(['-e', engine])

        cmd.extend(['--tpl-shell', template_payload])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        return {
            "output": result.stdout,
            "error": result.stderr,
            "base_url": base_url,
            "vulnerable_param": vulnerable_param,
            "template_payload": template_payload,
            "engine": engine,
            "exploitation_success": result.returncode == 0,
            "success": result.returncode == 0,
            "timestamp": time.time()
        }

    except Exception as e:
        return {
            "error": str(e),
            "base_url": base_url,
            "template_payload": template_payload,
            "success": False,
            "timestamp": time.time()
        }
