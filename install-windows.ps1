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

Write-Host "✅ Installation completed!" -ForegroundColor Green
Write-Host ""
Write-Host "🎯 Next steps:" -ForegroundColor Cyan
Write-Host "1. Run 'python main.py --create-config' to create configuration" -ForegroundColor White
Write-Host "2. Run 'python main.py --image your-app:latest' to start scanning" -ForegroundColor White
Write-Host ""
Write-Host "📖 Some tools may require additional setup - check the README" -ForegroundColor White
