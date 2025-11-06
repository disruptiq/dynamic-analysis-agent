#Requires -Version 5.1

Write-Host "🚀 Dynamic Analysis Agent - Windows Installation Script" -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor Green

# Check if running as administrator
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "❌ Please run this script as Administrator" -ForegroundColor Red
    exit 1
}

# Install Chocolatey if not present
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "📦 Installing Chocolatey..."
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
    refreshenv
}

# Install Python
Write-Host "🐍 Installing Python..."
choco install python -y

# Refresh environment
refreshenv

# Install security tools
Write-Host "🛡️ Installing security tools..."

# Nmap
Write-Host "Installing Nmap..."
choco install nmap -y

# Nikto (install manually or via other means)
Write-Host "⚠️ Nikto requires manual installation on Windows" -ForegroundColor Yellow
Write-Host "   Download from: https://github.com/sullo/nikto" -ForegroundColor Yellow

# SQLMap
Write-Host "Installing SQLMap..."
choco install sqlmap -y

# Install Python requirements
Write-Host "📚 Installing Python requirements..."
pip install -r requirements.txt

# OWASP ZAP
Write-Host "Installing OWASP ZAP..."
choco install zap -y

# Wireshark (for tcpdump-like functionality)
Write-Host "Installing Wireshark..."
choco install wireshark -y

# Install Kali Linux tools (where available)
Write-Host "🛡️ Installing Kali Linux tools..."

# Hydra
Write-Host "Installing Hydra..."
choco install hydra -y

# John the Ripper
Write-Host "Installing John the Ripper..."
choco install john -y

# Hashcat
Write-Host "Installing Hashcat..."
choco install hashcat -y

# Note about tools that require manual installation or WSL
Write-Host "⚠️ The following tools require manual installation or WSL on Windows:" -ForegroundColor Yellow
Write-Host "   - WPScan: gem install wpscan" -ForegroundColor Yellow
Write-Host "   - Joomlavs: https://github.com/rastating/joomlavs" -ForegroundColor Yellow
Write-Host "   - DNSRecon: pip install dnsrecon" -ForegroundColor Yellow
Write-Host "   - Enum4linux: pip install enum4linux-ng" -ForegroundColor Yellow
Write-Host "   - Responder: pip install Responder" -ForegroundColor Yellow
Write-Host "   - Bettercap: choco install bettercap" -ForegroundColor Yellow
Write-Host "   - Aircrack-ng: choco install aircrack-ng" -ForegroundColor Yellow
Write-Host "   - CrackMapExec: pip install crackmapexec" -ForegroundColor Yellow
Write-Host "   - Evil-WinRM: gem install evil-winrm" -ForegroundColor Yellow
Write-Host "   - Chisel: Download from GitHub releases" -ForegroundColor Yellow
Write-Host "   - Proxychains: choco install proxychains" -ForegroundColor Yellow
Write-Host "   - SQLNinja: Download from SourceForge" -ForegroundColor Yellow
Write-Host "   - Commix: pip install commix" -ForegroundColor Yellow
Write-Host "   - Tplmap: pip install tplmap" -ForegroundColor Yellow
Write-Host "   - Xsser: pip install xsser" -ForegroundColor Yellow
Write-Host "   - Patator: pip install patator" -ForegroundColor Yellow
Write-Host "   - Recon-ng: pip install recon-ng" -ForegroundColor Yellow
Write-Host "   - TheHarvester: pip install theharvester" -ForegroundColor Yellow
Write-Host "   - Amass: Download from GitHub releases" -ForegroundColor Yellow
Write-Host "   - Sublist3r: pip install sublist3r" -ForegroundColor Yellow
Write-Host "   - Go tools (Assetfinder, Httprobe, etc.): Install Go and use 'go install'" -ForegroundColor Yellow
Write-Host "   - Dotdotpwn: pip install dotdotpwn" -ForegroundColor Yellow
Write-Host "" -ForegroundColor Yellow
Write-Host "💡 Consider using WSL (Windows Subsystem for Linux) for full Kali tool compatibility" -ForegroundColor Cyan

Write-Host "✅ Installation completed!" -ForegroundColor Green
Write-Host ""
Write-Host "🎯 Next steps:" -ForegroundColor Cyan
Write-Host "1. Run 'python main.py --create-config' to create configuration" -ForegroundColor White
Write-Host "2. Run 'python main.py --image your-app:latest' to start scanning" -ForegroundColor White
Write-Host ""
Write-Host "📖 Some tools may require additional setup - check the README" -ForegroundColor White
