"""
Tool integrations for the Dynamic Analysis Agent.
"""

# Dynamic scanning tools
from .zap_scanner import start_zap, perform_zap_scan, stop_zap
from .nmap_scanner import perform_nmap_scan
from .nikto_scanner import perform_nikto_scan

# Vulnerability scanners (dynamic)
from .nessus_integration import perform_nessus_scan
from .openvas_integration import perform_openvas_scan
from .acunetix_integration import perform_acunetix_scan
from .qualysguard_integration import perform_qualysguard_scan
from .rapid7_nexpose_integration import perform_rapid7_nexpose_scan

# Exploitation tools
from .metasploit_integration import perform_metasploit_scan, run_metasploit_exploit, check_msfconsole_available
from .sqlmap_integration import perform_sqlmap_scan, sqlmap_dump_database, sqlmap_check_vulnerable

# Web scanning tools
from .gobuster_integration import perform_gobuster_scan, gobuster_directory_scan, gobuster_dns_scan
from .ffuf_integration import perform_ffuf_scan, ffuf_directory_fuzz, ffuf_parameter_fuzz, ffuf_subdomain_fuzz
from .nuclei_integration import perform_nuclei_scan, nuclei_cve_scan, nuclei_technology_scan, nuclei_exposed_panels_scan, nuclei_dns_scan
from .jaeles_integration import perform_jaeles_scan

# XSS tools
from .xsstrike_integration import perform_xsstrike_scan, xsstrike_get_payloads

# Parameter discovery
from .arjun_integration import perform_arjun_scan, arjun_get_parameters

# Runtime security
from .falco_integration import perform_falco_monitoring
from .ossec_integration import perform_ossec_scan

# Network security
from .snort_integration import perform_snort_analysis
from .suricata_integration import perform_suricata_analysis
from .wireshark_integration import perform_wireshark_capture
from .tcpdump_integration import perform_tcpdump_capture

# Browser exploitation
from .beef_integration import perform_beef_assessment

# Kali Linux tools
from .hydra_integration import perform_hydra_brute_force, perform_hydra_http_brute_force
from .wpscan_integration import perform_wpscan_scan, detect_wordpress
from .joomlavs_integration import perform_joomlavs_scan, detect_joomla
from .dnsrecon_integration import perform_dnsrecon_scan, perform_dnsrecon_zone_transfer
from .enum4linux_integration import perform_enum4linux_scan
from .responder_integration import perform_responder_poisoning
from .bettercap_integration import perform_bettercap_mitm, perform_bettercap_wireless_scan
from .aircrack_ng_integration import perform_aircrack_monitor, perform_aircrack_wpa_crack
from .john_ripper_integration import perform_john_crack, perform_john_benchmark
from .hashcat_integration import perform_hashcat_crack, perform_hashcat_benchmark, get_hashcat_hash_types
from .bloodhound_integration import perform_bloodhound_collection, analyze_bloodhound_data
from .crackmapexec_integration import perform_cme_smb_enum, perform_cme_pass_spray
from .evil_winrm_integration import perform_evil_winrm_connect, perform_evil_winrm_command
from .chisel_integration import perform_chisel_server, perform_chisel_client, stop_chisel_process
from .proxychains_integration import perform_proxychains_command, create_proxychains_config, perform_proxychains_nmap
from .sqlninja_integration import perform_sqlninja_scan, perform_sqlninja_data_extraction
from .commix_integration import perform_commix_scan, perform_commix_shell
from .tplmap_integration import perform_tplmap_scan, perform_tplmap_exploit
from .xsser_integration import perform_xsser_scan, perform_xsser_payload_test
from .patator_integration import perform_patator_brute_force, perform_patator_http_brute_force, perform_patator_service_brute_force
from .recon_ng_integration import perform_recon_ng_scan, get_recon_ng_modules
from .theharvester_integration import perform_theharvester_scan, perform_theharvester_email_harvest, perform_theharvester_subdomain_enum
from .maltego_integration import perform_maltego_transform, create_maltego_graph, analyze_relationships
from .shodan_integration import perform_shodan_search, perform_shodan_host_lookup, correlate_vulnerabilities
from .amass_integration import perform_amass_scan, perform_amass_intel
from .sublist3r_integration import perform_sublist3r_scan, get_sublist3r_engines
from .assetfinder_integration import perform_assetfinder_scan, perform_assetfinder_company
from .httprobe_integration import perform_httprobe_scan, perform_httprobe_prefer_https
from .gf_integration import perform_gf_scan, get_gf_patterns
from .qsreplace_integration import perform_qsreplace_replacement, perform_qsreplace_fuzz
from .ferret_integration import perform_ferret_scan, perform_ferret_wordlist_scan
from .dotdotpwn_integration import perform_dotdotpwn_scan, perform_dotdotpwn_traversal_test

__all__ = [
    # Dynamic scanning tools
    'start_zap', 'perform_zap_scan', 'stop_zap',
    'perform_nmap_scan',
    'perform_nikto_scan',

    # Vulnerability scanners (dynamic)
    'perform_nessus_scan',
    'perform_openvas_scan',
    'perform_acunetix_scan',
    'perform_qualysguard_scan',
    'perform_rapid7_nexpose_scan',

    # Exploitation tools
    'perform_metasploit_scan', 'run_metasploit_exploit', 'check_msfconsole_available',
    'perform_sqlmap_scan', 'sqlmap_dump_database', 'sqlmap_check_vulnerable',

    # Web scanning tools
    'perform_gobuster_scan', 'gobuster_directory_scan', 'gobuster_dns_scan',
    'perform_ffuf_scan', 'ffuf_directory_fuzz', 'ffuf_parameter_fuzz', 'ffuf_subdomain_fuzz',
    'perform_nuclei_scan', 'nuclei_cve_scan', 'nuclei_technology_scan', 'nuclei_exposed_panels_scan', 'nuclei_dns_scan',
    'perform_jaeles_scan',

    # XSS tools
    'perform_xsstrike_scan', 'xsstrike_get_payloads',

    # Parameter discovery
    'perform_arjun_scan', 'arjun_get_parameters',

    # Runtime security
    'perform_falco_monitoring',
    'perform_ossec_scan',

    # Network security
    'perform_snort_analysis',
    'perform_suricata_analysis',
    'perform_wireshark_capture',
    'perform_tcpdump_capture',

    # Browser exploitation
    'perform_beef_assessment',

    # Kali Linux tools
    'perform_hydra_brute_force', 'perform_hydra_http_brute_force',
    'perform_wpscan_scan', 'detect_wordpress',
    'perform_joomlavs_scan', 'detect_joomla',
    'perform_dnsrecon_scan', 'perform_dnsrecon_zone_transfer',
    'perform_enum4linux_scan',
    'perform_responder_poisoning',
    'perform_bettercap_mitm', 'perform_bettercap_wireless_scan',
    'perform_aircrack_monitor', 'perform_aircrack_wpa_crack',
    'perform_john_crack', 'perform_john_benchmark',
    'perform_hashcat_crack', 'perform_hashcat_benchmark', 'get_hashcat_hash_types',
    'perform_bloodhound_collection', 'analyze_bloodhound_data',
    'perform_cme_smb_enum', 'perform_cme_pass_spray',
    'perform_evil_winrm_connect', 'perform_evil_winrm_command',
    'perform_chisel_server', 'perform_chisel_client', 'stop_chisel_process',
    'perform_proxychains_command', 'create_proxychains_config', 'perform_proxychains_nmap',
    'perform_sqlninja_scan', 'perform_sqlninja_data_extraction',
    'perform_commix_scan', 'perform_commix_shell',
    'perform_tplmap_scan', 'perform_tplmap_exploit',
    'perform_xsser_scan', 'perform_xsser_payload_test',
    'perform_patator_brute_force', 'perform_patator_http_brute_force', 'perform_patator_service_brute_force',
    'perform_recon_ng_scan', 'get_recon_ng_modules',
    'perform_theharvester_scan', 'perform_theharvester_email_harvest', 'perform_theharvester_subdomain_enum',
    'perform_maltego_transform', 'create_maltego_graph', 'analyze_relationships',
    'perform_shodan_search', 'perform_shodan_host_lookup', 'correlate_vulnerabilities',
    'perform_amass_scan', 'perform_amass_intel',
    'perform_sublist3r_scan', 'get_sublist3r_engines',
    'perform_assetfinder_scan', 'perform_assetfinder_company',
    'perform_httprobe_scan', 'perform_httprobe_prefer_https',
    'perform_gf_scan', 'get_gf_patterns',
    'perform_qsreplace_replacement', 'perform_qsreplace_fuzz',
    'perform_ferret_scan', 'perform_ferret_wordlist_scan',
    'perform_dotdotpwn_scan', 'perform_dotdotpwn_traversal_test'
]
