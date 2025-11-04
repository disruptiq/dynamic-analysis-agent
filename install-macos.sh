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

# Install Python requirements
echo "📚 Installing Python requirements..."
pip3 install -r requirements.txt

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
