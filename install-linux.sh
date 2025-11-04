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
sudo apt-get install -y curl wget git unzip openjdk-11-jdk tcpdump

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
sudo apt-get install -y nuclei

# Arjun
echo "Installing Arjun..."
sudo apt-get install -y arjun

# Install Python requirements
echo "📚 Installing Python requirements..."
pip3 install -r requirements.txt

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
