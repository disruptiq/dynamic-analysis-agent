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
    'perform_beef_assessment'
]
