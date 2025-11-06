#!/bin/bash

echo "🚀 Dynamic Analysis Agent - macOS Installation Script"
echo "====================================================="

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "📦 Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Update Homebrew
echo "📦 Updating Homebrew..."
brew update

# Install Python
echo "🐍 Installing Python..."
brew install python

# Install security tools
echo "🛡️ Installing security tools..."

# Nmap
echo "Installing Nmap..."
brew install nmap

# Nikto
echo "Installing Nikto..."
brew install nikto

# SQLMap
echo "Installing SQLMap..."
brew install sqlmap

# Gobuster
echo "Installing Gobuster..."
brew install gobuster

# FFUF
echo "Installing FFUF..."
brew install ffuf

# Nuclei
echo "Installing Nuclei..."
brew install nuclei

# Arjun
echo "Installing Arjun..."
brew install arjun

# Install Kali Linux tools
echo "🛡️ Installing Kali Linux tools..."

# Hydra
echo "Installing Hydra..."
brew install hydra

# WPScan
echo "Installing WPScan..."
brew install wpscan

# Joomlavs
echo "Installing Joomlavs..."
brew install joomlavs

# DNSRecon
echo "Installing DNSRecon..."
pip3 install dnsrecon

# Enum4linux
echo "Installing Enum4linux..."
brew install enum4linux

# Responder
echo "Installing Responder..."
pip3 install responder

# Bettercap
echo "Installing Bettercap..."
brew install bettercap

# Aircrack-ng
echo "Installing Aircrack-ng..."
brew install aircrack-ng

# John the Ripper
echo "Installing John the Ripper..."
brew install john-jumbo

# Hashcat
echo "Installing Hashcat..."
brew install hashcat

# CrackMapExec
echo "Installing CrackMapExec..."
pip3 install crackmapexec

# Evil-WinRM
echo "Installing Evil-WinRM..."
gem install evil-winrm

# Chisel
echo "Installing Chisel..."
brew install chisel

# Proxychains
echo "Installing Proxychains..."
brew install proxychains-ng

# SQLNinja
echo "Installing SQLNinja..."
brew install sqlninja

# Commix
echo "Installing Commix..."
pip3 install commix

# Tplmap
echo "Installing Tplmap..."
pip3 install tplmap

# Xsser
echo "Installing Xsser..."
pip3 install xsser

# Patator
echo "Installing Patator..."
pip3 install patator

# Recon-ng
echo "Installing Recon-ng..."
pip3 install recon-ng

# TheHarvester
echo "Installing TheHarvester..."
pip3 install theharvester

# Amass
echo "Installing Amass..."
brew install amass

# Sublist3r
echo "Installing Sublist3r..."
pip3 install sublist3r

# Go tools (Assetfinder, Httprobe, Gf, Qsreplace, Ferret)
echo "Installing Go tools..."
brew install go

# Assetfinder
echo "Installing Assetfinder..."
go install github.com/tomnomnom/assetfinder@latest
cp ~/go/bin/assetfinder /usr/local/bin/

# Httprobe
echo "Installing Httprobe..."
go install github.com/tomnomnom/httprobe@latest
cp ~/go/bin/httprobe /usr/local/bin/

# Gf
echo "Installing Gf..."
go install github.com/tomnomnom/gf@latest
cp ~/go/bin/gf /usr/local/bin/
# Install gf patterns
git clone https://github.com/1ndianl33t/Gf-Patterns.git ~/.gf

# Qsreplace
echo "Installing Qsreplace..."
go install github.com/tomnomnom/qsreplace@latest
cp ~/go/bin/qsreplace /usr/local/bin/

# Ferret
echo "Installing Ferret..."
go install github.com/Montferret/ferret@latest
cp ~/go/bin/ferret /usr/local/bin/

# Dotdotpwn
echo "Installing Dotdotpwn..."
pip3 install dotdotpwn

# Install Python requirements
echo "📚 Installing Python requirements..."
pip3 install -r requirements.txt

# Install Shodan (Python library)
echo "Installing Shodan Python library..."
pip3 install shodan

# Install OWASP ZAP (manual installation required)
echo "⚠️  OWASP ZAP requires manual installation on macOS"
echo "   Download from: https://www.zaproxy.org/download/"
echo "   Add zap.sh to your PATH"

# Install Metasploit (optional)
read -p "🤔 Do you want to install Metasploit Framework? (y/N): " install_msf
if [[ $install_msf =~ ^[Yy]$ ]]; then
    echo "Installing Metasploit Framework..."
    brew install metasploit
fi

echo "✅ Installation completed!"
echo ""
echo "🎯 Next steps:"
echo "1. Run 'python3 main.py --create-config' to create configuration"
echo "2. Run 'python3 main.py --image your-app:latest' to start scanning"
echo ""
echo "📖 Some tools may require additional setup - check the README"
