#!/bin/bash

echo "🚀 Dynamic Analysis Agent - Linux Installation Script"
echo "======================================================"

# Update package list
echo "📦 Updating package list..."
sudo apt-get update

# Install Python and pip
echo "🐍 Installing Python dependencies..."
sudo apt-get install -y python3 python3-pip python3-dev

# Install system dependencies
echo "🔧 Installing system dependencies..."
sudo apt-get install -y curl wget git unzip openjdk-11-jdk tcpdump golang-go

# Setup Go environment
export PATH=$PATH:/usr/local/go/bin
export GOPATH=$HOME/go
export GOROOT=/usr/local/go
export PATH=$PATH:$GOPATH/bin

# Install security tools
echo "🛡️ Installing security tools..."

# Nmap
echo "Installing Nmap..."
sudo apt-get install -y nmap

# Nikto
echo "Installing Nikto..."
sudo apt-get install -y nikto

# SQLMap
echo "Installing SQLMap..."
sudo apt-get install -y sqlmap

# Gobuster
echo "Installing Gobuster..."
sudo apt-get install -y gobuster

# FFUF
echo "Installing FFUF..."
sudo apt-get install -y ffuf

# Nuclei
echo "Installing Nuclei..."
wget https://github.com/projectdiscovery/nuclei/releases/download/v3.4.10/nuclei_3.4.10_linux_amd64.tar.gz
tar -xzf nuclei_3.4.10_linux_amd64.tar.gz
sudo mv nuclei /usr/local/bin/nuclei
rm nuclei_3.4.10_linux_amd64.tar.gz

# Arjun
echo "Installing Arjun..."
sudo apt-get install -y arjun

# Install Kali Linux tools
echo "🛡️ Installing Kali Linux tools..."

# Hydra
echo "Installing Hydra..."
sudo apt-get install -y hydra

# WPScan
echo "Installing WPScan..."
sudo apt-get install -y ruby ruby-dev
sudo gem install wpscan

# Joomlavs
echo "Installing Joomlavs..."
git clone https://github.com/rastating/joomlavs.git /opt/joomlavs
cd /opt/joomlavs
sudo chmod +x joomlavs.rb
sudo ln -s /opt/joomlavs/joomlavs.rb /usr/local/bin/joomlavs

# DNSRecon
echo "Installing DNSRecon..."
sudo apt-get install -y dnsrecon

# Enum4linux
echo "Installing Enum4linux..."
sudo apt-get install -y enum4linux

# Responder
echo "Installing Responder..."
git clone https://github.com/lgandx/Responder.git /opt/responder
sudo ln -s /opt/responder/Responder.py /usr/local/bin/responder

# Bettercap
echo "Installing Bettercap..."
sudo apt-get install -y bettercap

# Aircrack-ng
echo "Installing Aircrack-ng..."
sudo apt-get install -y aircrack-ng

# John the Ripper
echo "Installing John the Ripper..."
sudo apt-get install -y john

# Hashcat
echo "Installing Hashcat..."
sudo apt-get install -y hashcat

# CrackMapExec
echo "Installing CrackMapExec..."
sudo apt-get install -y crackmapexec

# Evil-WinRM
echo "Installing Evil-WinRM..."
sudo gem install evil-winrm

# Chisel
echo "Installing Chisel..."
wget https://github.com/jpillora/chisel/releases/download/v1.7.7/chisel_1.7.7_linux_amd64.gz
gunzip chisel_1.7.7_linux_amd64.gz
sudo chmod +x chisel
sudo mv chisel /usr/local/bin/

# Proxychains
echo "Installing Proxychains..."
sudo apt-get install -y proxychains

# SQLNinja
echo "Installing SQLNinja..."
sudo apt-get install -y sqlninja

# Commix
echo "Installing Commix..."
git clone https://github.com/commixproject/commix.git /opt/commix
sudo ln -s /opt/commix/commix.py /usr/local/bin/commix

# Tplmap
echo "Installing Tplmap..."
git clone https://github.com/epinna/tplmap.git /opt/tplmap
cd /opt/tplmap
sudo pip3 install -r requirements.txt
sudo ln -s /opt/tplmap/tplmap.py /usr/local/bin/tplmap

# Xsser
echo "Installing Xsser..."
sudo apt-get install -y xsser

# Patator
echo "Installing Patator..."
sudo apt-get install -y patator

# Recon-ng
echo "Installing Recon-ng..."
git clone https://github.com/lanmaster53/recon-ng.git /opt/recon-ng
cd /opt/recon-ng
sudo pip3 install -r REQUIREMENTS
sudo ln -s /opt/recon-ng/recon-ng /usr/local/bin/recon-ng

# TheHarvester
echo "Installing TheHarvester..."
git clone https://github.com/laramies/theHarvester.git /opt/theharvester
cd /opt/theharvester
sudo pip3 install -r requirements.txt
sudo ln -s /opt/theharvester/theHarvester.py /usr/local/bin/theHarvester

# Amass
echo "Installing Amass..."
wget https://github.com/OWASP/Amass/releases/download/v3.21.2/amass_linux_amd64.zip
unzip amass_linux_amd64.zip
sudo mv amass_linux_amd64/amass /usr/local/bin/
rm -rf amass_linux_amd64*

# Sublist3r
echo "Installing Sublist3r..."
git clone https://github.com/aboul3la/Sublist3r.git /opt/sublist3r
cd /opt/sublist3r
sudo pip3 install -r requirements.txt
sudo ln -s /opt/sublist3r/sublist3r.py /usr/local/bin/sublist3r

# Assetfinder
echo "Installing Assetfinder..."
go install github.com/tomnomnom/assetfinder@latest
sudo cp ~/go/bin/assetfinder /usr/local/bin/

# Httprobe
echo "Installing Httprobe..."
go install github.com/tomnomnom/httprobe@latest
sudo cp ~/go/bin/httprobe /usr/local/bin/

# Gf
echo "Installing Gf..."
go install github.com/tomnomnom/gf@latest
sudo cp ~/go/bin/gf /usr/local/bin/
# Install gf patterns
git clone https://github.com/1ndianl33t/Gf-Patterns.git ~/.gf

# Qsreplace
echo "Installing Qsreplace..."
go install github.com/tomnomnom/qsreplace@latest
sudo cp ~/go/bin/qsreplace /usr/local/bin/

# Ferret
echo "Installing Ferret..."
go install github.com/Montferret/ferret@latest
sudo cp ~/go/bin/ferret /usr/local/bin/

# Dotdotpwn
echo "Installing Dotdotpwn..."
sudo apt-get install -y dotdotpwn

# Install Python requirements
echo "📚 Installing Python requirements..."
pip3 install -r requirements.txt

# Install Shodan (Python library)
echo "Installing Shodan Python library..."
pip3 install shodan

# Install OWASP ZAP (optional - large download)
read -p "🤔 Do you want to install OWASP ZAP? (y/N): " install_zap
if [[ $install_zap =~ ^[Yy]$ ]]; then
    echo "Installing OWASP ZAP..."
    wget https://github.com/zaproxy/zaproxy/releases/download/v2.12.0/ZAP_2.12.0_Linux.tar.gz
    tar -xzf ZAP_2.12.0_Linux.tar.gz
    sudo mv ZAP_2.12.0 /opt/zap
    sudo ln -s /opt/zap/zap.sh /usr/local/bin/zap.sh
    rm ZAP_2.12.0_Linux.tar.gz
fi

# Install Metasploit (optional - very large)
read -p "🤔 Do you want to install Metasploit Framework? (y/N): " install_msf
if [[ $install_msf =~ ^[Yy]$ ]]; then
    echo "Installing Metasploit Framework..."
    curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall
    chmod 755 msfinstall
    sudo ./msfinstall
    rm msfinstall
fi

echo "✅ Installation completed!"
echo ""
echo "🎯 Next steps:"
echo "1. Run 'python3 main.py --create-config' to create configuration"
echo "2. Run 'python3 main.py --image your-app:latest' to start scanning"
echo ""
echo "📖 For full functionality, ensure all tools are in your PATH"
