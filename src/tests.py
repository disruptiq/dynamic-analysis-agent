"""
Test execution functions for the Dynamic Analysis Agent.
"""

import time
import requests

from .vulnerability_scanner_main import test_vulnerabilities
from .tools import (
    start_zap, perform_zap_scan, stop_zap,
    perform_nmap_scan, perform_nikto_scan,
    perform_hydra_brute_force, perform_hydra_http_brute_force,
    perform_wpscan_scan, detect_wordpress,
    perform_joomlavs_scan, detect_joomla,
    perform_dnsrecon_scan, perform_dnsrecon_zone_transfer,
    perform_enum4linux_scan,
    perform_responder_poisoning,
    perform_bettercap_mitm, perform_bettercap_wireless_scan,
    perform_aircrack_monitor, perform_aircrack_wpa_crack,
    perform_john_crack, perform_john_benchmark,
    perform_hashcat_crack, perform_hashcat_benchmark, get_hashcat_hash_types,
    perform_bloodhound_collection, analyze_bloodhound_data,
    perform_cme_smb_enum, perform_cme_pass_spray,
    perform_evil_winrm_connect, perform_evil_winrm_command,
    perform_chisel_server, perform_chisel_client, stop_chisel_process,
    perform_proxychains_command, create_proxychains_config, perform_proxychains_nmap,
    perform_sqlninja_scan, perform_sqlninja_data_extraction,
    perform_commix_scan, perform_commix_shell,
    perform_tplmap_scan, perform_tplmap_exploit,
    perform_xsser_scan, perform_xsser_payload_test,
    perform_patator_brute_force, perform_patator_http_brute_force, perform_patator_service_brute_force,
    perform_recon_ng_scan, get_recon_ng_modules,
    perform_theharvester_scan, perform_theharvester_email_harvest, perform_theharvester_subdomain_enum,
    perform_maltego_transform, create_maltego_graph, analyze_relationships,
    perform_shodan_search, perform_shodan_host_lookup, correlate_vulnerabilities,
    perform_amass_scan, perform_amass_intel,
    perform_sublist3r_scan, get_sublist3r_engines,
    perform_assetfinder_scan, perform_assetfinder_company,
    perform_httprobe_scan, perform_httprobe_prefer_https,
    perform_gf_scan, get_gf_patterns,
    perform_qsreplace_replacement, perform_qsreplace_fuzz,
    perform_ferret_scan, perform_ferret_wordlist_scan,
    perform_dotdotpwn_scan, perform_dotdotpwn_traversal_test
)
from .logger import logger
from .progress import ScanProgress


def perform_basic_tests(ports, zap_port=8090):
    """
    Perform basic dynamic cybersecurity tests on multiple ports.

    Args:
    ports (list): List of ports the application is running on
    zap_port (int): ZAP API port

    Returns:
        dict: Scan results with vulnerabilities and metadata
    """
    results = {
        "targets": [f"http://localhost:{port}" for port in ports],
    "timestamp": time.time(),
    "vulnerabilities": [],
    "tools": [],
    "summary": {}
    }

    # Initialize progress tracking
    progress = ScanProgress(total_steps=28, description="Dynamic Analysis Scan")
    progress.start()

    logger.info(f"Starting dynamic analysis on ports: {ports}")
    progress.update(description="Checking connectivity")

    # Wait for application to start up
    logger.info("Waiting for application to start...")
    time.sleep(5)

    # Basic connectivity test for each port
    connectivity_results = {}
    for port in ports:
        base_url = f"http://localhost:{port}"
        connectivity_ok = False
        try:
            response = requests.get(base_url, timeout=10)
            logger.info(f"Port {port} - Basic connectivity: Status {response.status_code}")
            if response.status_code >= 200 and response.status_code < 300:
                logger.info(f"SUCCESS: Application on port {port} is responding")
                connectivity_ok = True
            else:
                logger.warning(f"✗ Port {port} returned error status")
        except requests.RequestException as e:
            logger.error(f"✗ Failed to connect to port {port}: {e}")
        connectivity_results[port] = connectivity_ok

    results["connectivity"] = connectivity_results
    # Continue if at least one port is accessible
    any_connectivity = any(connectivity_results.values())
    progress.update()

    if not any_connectivity:
        progress.finish()
        return results

    # Test for common vulnerabilities on all accessible ports
    progress.update(description="Testing vulnerabilities")
    all_vulnerabilities = []
    for port in ports:
        if connectivity_results.get(port, False):
            base_url = f"http://localhost:{port}"
            logger.info(f"Starting vulnerability assessment on {base_url}")
            vulnerabilities = test_vulnerabilities(base_url)
            # Add port information to vulnerabilities
            for vuln in vulnerabilities:
                vuln['port'] = port
            all_vulnerabilities.extend(vulnerabilities)
            logger.info(f"Vulnerability assessment on port {port} completed: found {len(vulnerabilities)} potential issues")

    results["vulnerabilities"].extend(all_vulnerabilities)
    progress.update()

    # Perform Nmap scan on all ports
    progress.update(description="Running Nmap scan")
    logger.info("Starting Nmap network scan")
    nmap_results = perform_nmap_scan("localhost", ports)
    if nmap_results:
        results["tools"].append({"name": "nmap", "results": nmap_results})
        logger.info("Nmap scan completed")
    else:
        logger.info("Nmap scan skipped or not available")
    progress.update()

    # Perform Nikto scan on all accessible ports
    progress.update(description="Running Nikto scan")
    logger.info("Starting Nikto web server scan")
    all_nikto_results = []
    for port in ports:
        if connectivity_results.get(port, False):
            base_url = f"http://localhost:{port}"
            nikto_results = perform_nikto_scan(base_url)
            if nikto_results:
                nikto_results['port'] = port  # Add port info
                all_nikto_results.append(nikto_results)
                logger.info(f"Nikto scan on port {port} completed")
            else:
                logger.info(f"Nikto scan on port {port} skipped or not available")

    if all_nikto_results:
        results["tools"].append({"name": "nikto", "results": all_nikto_results})
    progress.update()

    # Perform ZAP scan on all accessible ports
    progress.update(description="Running OWASP ZAP scan")
    logger.info("Starting OWASP ZAP security scan")
    all_zap_results = []
    for port in ports:
        if connectivity_results.get(port, False):
            base_url = f"http://localhost:{port}"
            zap_results = perform_zap_scan(base_url, zap_port)
            if zap_results:
                zap_results['port'] = port  # Add port info
                all_zap_results.append(zap_results)
                logger.info(f"ZAP scan on port {port} completed")
            else:
                logger.info(f"ZAP scan on port {port} skipped or not available")

    if all_zap_results:
        results["tools"].append({"name": "zap", "results": all_zap_results})
    progress.update()

    # Perform Hydra brute force on accessible ports
    progress.update(description="Running Hydra brute force")
    logger.info("Starting Hydra brute force testing")
    all_hydra_results = []
    for port in ports:
        if connectivity_results.get(port, False):
            base_url = f"http://localhost:{port}"
            hydra_results = perform_hydra_http_brute_force(base_url)
            if hydra_results:
                hydra_results['port'] = port
                all_hydra_results.append(hydra_results)
                logger.info(f"Hydra brute force on port {port} completed")
            else:
                logger.info(f"Hydra brute force on port {port} skipped or not available")

    if all_hydra_results:
        results["tools"].append({"name": "hydra", "results": all_hydra_results})
    progress.update()

    # Perform CMS-specific scans on accessible ports
    progress.update(description="Checking for CMS installations")
    logger.info("Checking for WordPress and Joomla installations")
    cms_results = []
    for port in ports:
        if connectivity_results.get(port, False):
            base_url = f"http://localhost:{port}"

            # Check for WordPress
            if detect_wordpress(base_url):
                logger.info(f"WordPress detected on port {port}, running WPScan")
                wpscan_results = perform_wpscan_scan(base_url, enumerate_users=True)
                if wpscan_results:
                    wpscan_results['port'] = port
                    wpscan_results['cms'] = 'wordpress'
                    cms_results.append(wpscan_results)

            # Check for Joomla
            elif detect_joomla(base_url):
                logger.info(f"Joomla detected on port {port}, running Joomlavs")
                joomlavs_results = perform_joomlavs_scan(base_url)
                if joomlavs_results:
                    joomlavs_results['port'] = port
                    joomlavs_results['cms'] = 'joomla'
                    cms_results.append(joomlavs_results)

    results["tools"].append({"name": "cms_scanners", "results": cms_results})
    progress.update()

    # Perform Recon-ng reconnaissance on accessible ports
    progress.update(description="Running Recon-ng reconnaissance")
    logger.info("Starting Recon-ng web reconnaissance")
    all_recon_results = []
    for port in ports:
        if connectivity_results.get(port, False):
            base_url = f"http://localhost:{port}"
            recon_results = perform_recon_ng_scan(base_url)
            if recon_results:
                recon_results['port'] = port
                all_recon_results.append(recon_results)
                logger.info(f"Recon-ng scan on port {port} completed")
            else:
                logger.info(f"Recon-ng scan on port {port} skipped or not available")

    if all_recon_results:
        results["tools"].append({"name": "recon_ng", "results": all_recon_results})
    progress.update()

    # Perform TheHarvester OSINT gathering
    progress.update(description="Running TheHarvester OSINT")
    logger.info("Starting TheHarvester OSINT gathering")
    # TheHarvester can work on domains, but for localhost, perhaps skip or use localhost
    # For demo, we'll skip or use a placeholder
    theharvester_results = perform_theharvester_scan("localhost")
    if theharvester_results:
        results["tools"].append({"name": "theharvester", "results": theharvester_results})
        logger.info("TheHarvester scan completed")
    else:
        logger.info("TheHarvester scan skipped or not available")
    progress.update()

    # Perform Patator brute force on accessible ports
    progress.update(description="Running Patator brute force")
    logger.info("Starting Patator brute force testing")
    all_patator_results = []
    for port in ports:
        if connectivity_results.get(port, False):
            base_url = f"http://localhost:{port}"
            patator_results = perform_patator_http_brute_force(base_url)
            if patator_results:
                patator_results['port'] = port
                all_patator_results.append(patator_results)
                logger.info(f"Patator brute force on port {port} completed")
            else:
                logger.info(f"Patator brute force on port {port} skipped or not available")

    if all_patator_results:
        results["tools"].append({"name": "patator", "results": all_patator_results})
    progress.update()

    # Perform XSSer scan on accessible ports
    progress.update(description="Running XSSer XSS testing")
    logger.info("Starting XSSer XSS vulnerability testing")
    all_xsser_results = []
    for port in ports:
        if connectivity_results.get(port, False):
            base_url = f"http://localhost:{port}"
            xsser_results = perform_xsser_scan(base_url)
            if xsser_results:
                xsser_results['port'] = port
                all_xsser_results.append(xsser_results)
                logger.info(f"XSSer scan on port {port} completed")
            else:
                logger.info(f"XSSer scan on port {port} skipped or not available")

    if all_xsser_results:
        results["tools"].append({"name": "xsser", "results": all_xsser_results})
    progress.update()

    # Perform Tplmap template injection testing on accessible ports
    progress.update(description="Running Tplmap template injection testing")
    logger.info("Starting Tplmap template injection testing")
    all_tplmap_results = []
    for port in ports:
        if connectivity_results.get(port, False):
            base_url = f"http://localhost:{port}"
            tplmap_results = perform_tplmap_scan(base_url)
            if tplmap_results:
                tplmap_results['port'] = port
                all_tplmap_results.append(tplmap_results)
                logger.info(f"Tplmap scan on port {port} completed")
            else:
                logger.info(f"Tplmap scan on port {port} skipped or not available")

    if all_tplmap_results:
        results["tools"].append({"name": "tplmap", "results": all_tplmap_results})
    progress.update()

    # Perform Commix command injection testing on accessible ports
    progress.update(description="Running Commix command injection testing")
    logger.info("Starting Commix command injection testing")
    all_commix_results = []
    for port in ports:
        if connectivity_results.get(port, False):
            base_url = f"http://localhost:{port}"
            commix_results = perform_commix_scan(base_url)
            if commix_results:
                commix_results['port'] = port
                all_commix_results.append(commix_results)
                logger.info(f"Commix scan on port {port} completed")
            else:
                logger.info(f"Commix scan on port {port} skipped or not available")

    if all_commix_results:
        results["tools"].append({"name": "commix", "results": all_commix_results})
    progress.update()

    # Perform SQLNinja SQL injection testing on accessible ports
    progress.update(description="Running SQLNinja SQL injection testing")
    logger.info("Starting SQLNinja SQL injection testing")
    all_sqlninja_results = []
    for port in ports:
        if connectivity_results.get(port, False):
            base_url = f"http://localhost:{port}"
            sqlninja_results = perform_sqlninja_scan(base_url)
            if sqlninja_results:
                sqlninja_results['port'] = port
                all_sqlninja_results.append(sqlninja_results)
                logger.info(f"SQLNinja scan on port {port} completed")
            else:
                logger.info(f"SQLNinja scan on port {port} skipped or not available")

    results["tools"].append({"name": "sqlninja", "results": all_sqlninja_results})
    progress.update()

    # Perform Amass subdomain enumeration
    progress.update(description="Running Amass subdomain enumeration")
    logger.info("Starting Amass subdomain enumeration")
    # For demo purposes, use localhost as domain (though not ideal)
    amass_results = perform_amass_scan("localhost")
    if amass_results:
        results["tools"].append({"name": "amass", "results": amass_results})
        logger.info("Amass scan completed")
    else:
        logger.info("Amass scan skipped or not available")
    progress.update()

    # Perform Sublist3r subdomain enumeration
    progress.update(description="Running Sublist3r subdomain enumeration")
    logger.info("Starting Sublist3r subdomain enumeration")
    sublist3r_results = perform_sublist3r_scan("localhost")
    if sublist3r_results:
        results["tools"].append({"name": "sublist3r", "results": sublist3r_results})
        logger.info("Sublist3r scan completed")
    else:
        logger.info("Sublist3r scan skipped or not available")
    progress.update()

    # Perform Assetfinder asset discovery
    progress.update(description="Running Assetfinder asset discovery")
    logger.info("Starting Assetfinder asset discovery")
    assetfinder_results = perform_assetfinder_scan("localhost")
    if assetfinder_results:
        results["tools"].append({"name": "assetfinder", "results": assetfinder_results})
        logger.info("Assetfinder scan completed")
    else:
        logger.info("Assetfinder scan skipped or not available")
    progress.update()

    # Perform Httprobe HTTP probing (using dummy domains for demo)
    progress.update(description="Running Httprobe HTTP probing")
    logger.info("Starting Httprobe HTTP probing")
    dummy_domains = ["localhost"]  # In real use, would use discovered subdomains
    httprobe_results = perform_httprobe_scan(dummy_domains)
    if httprobe_results:
        results["tools"].append({"name": "httprobe", "results": httprobe_results})
        logger.info("Httprobe scan completed")
    else:
        logger.info("Httprobe scan skipped or not available")
    progress.update()

    # Perform Gf pattern matching on vulnerability scan results
    progress.update(description="Running Gf pattern matching")
    logger.info("Starting Gf pattern matching")
    # Use the vulnerability results as content to scan for patterns
    vuln_content = "\n".join([str(vuln) for vuln in results.get("vulnerabilities", [])])
    gf_results = perform_gf_scan(vuln_content)
    if gf_results:
        results["tools"].append({"name": "gf", "results": gf_results})
        logger.info("Gf scan completed")
    else:
        logger.info("Gf scan skipped or not available")
    progress.update()

    # Perform Qsreplace query string fuzzing
    progress.update(description="Running Qsreplace query string fuzzing")
    logger.info("Starting Qsreplace query string fuzzing")
    # Create some sample URLs for testing
    sample_urls = [f"http://localhost:{port}/?param=test" for port in ports if connectivity_results.get(port, False)]
    if sample_urls:
        qsreplace_results = perform_qsreplace_replacement(sample_urls, "FUZZ")
        if qsreplace_results:
            results["tools"].append({"name": "qsreplace", "results": qsreplace_results})
            logger.info("Qsreplace scan completed")
        else:
            logger.info("Qsreplace scan skipped or not available")
    else:
        logger.info("No accessible URLs for Qsreplace testing")
    progress.update()

    # Perform Ferret file disclosure testing
    progress.update(description="Running Ferret file disclosure testing")
    logger.info("Starting Ferret file disclosure testing")
    all_ferret_results = []
    for port in ports:
        if connectivity_results.get(port, False):
            base_url = f"http://localhost:{port}"
            ferret_results = perform_ferret_scan(base_url)
            if ferret_results:
                ferret_results['port'] = port
                all_ferret_results.append(ferret_results)
                logger.info(f"Ferret scan on port {port} completed")
            else:
                logger.info(f"Ferret scan on port {port} skipped or not available")

    if all_ferret_results:
        results["tools"].append({"name": "ferret", "results": all_ferret_results})
    progress.update()

    # Perform Dotdotpwn directory traversal testing
    progress.update(description="Running Dotdotpwn directory traversal testing")
    logger.info("Starting Dotdotpwn directory traversal testing")
    all_dotdotpwn_results = []
    for port in ports:
        if connectivity_results.get(port, False):
            base_url = f"http://localhost:{port}"
            dotdotpwn_results = perform_dotdotpwn_scan(base_url)
            if dotdotpwn_results:
                dotdotpwn_results['port'] = port
                all_dotdotpwn_results.append(dotdotpwn_results)
                logger.info(f"Dotdotpwn scan on port {port} completed")
            else:
                logger.info(f"Dotdotpwn scan on port {port} skipped or not available")

    if all_dotdotpwn_results:
        results["tools"].append({"name": "dotdotpwn", "results": all_dotdotpwn_results})
    progress.update(description="Generating summary")

    # Generate summary
    vuln_types = {}
    for vuln in results["vulnerabilities"]:
        vuln_type = vuln.get("type", "Unknown")
        vuln_types[vuln_type] = vuln_types.get(vuln_type, 0) + 1

    results["summary"] = {
    "total_vulnerabilities": len(results["vulnerabilities"]),
    "vulnerability_types": vuln_types,
    "tools_run": len(results["tools"]),
    "ports_scanned": len(ports),
        "scan_duration": time.time() - results["timestamp"]
    }

    progress.finish()
    logger.info(f"Scan completed. Found {len(results['vulnerabilities'])} vulnerabilities across {len(results['tools'])} tools on {len(ports)} ports.")
    logger.debug(f"Scan duration: {results['summary']['scan_duration']:.2f} seconds")
    return results
