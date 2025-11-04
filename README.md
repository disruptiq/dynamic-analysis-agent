# Dynamic Analysis Agent

A cybersecurity tool for performing dynamic analysis tests on applications running in sandboxed Docker containers.

## Features

- Automated Docker container setup and management
- Basic connectivity testing
- Vulnerability scanning for common web security issues:
  - Cross-Site Scripting (XSS)
  - Directory Traversal
- Integration with industry-standard security tools:
  - OWASP ZAP for comprehensive web application scanning
  - Nmap for port scanning and service enumeration
  - Nikto for web server vulnerability detection

## Installation

1. Ensure Docker is installed and running on your system.
2. Install the following security tools (optional, but recommended for full functionality):
   - [OWASP ZAP](https://www.zaproxy.org/download/) - Download and ensure `zap.sh` is in your PATH
   - [Nmap](https://nmap.org/download.html) - Install via package manager or download
   - [Nikto](https://github.com/sullo/nikto) - Install via package manager or download
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the analysis agent with a Docker image:

```bash
python main.py --image your-app:latest
```

Or run from the project directory:

```bash
cd dynamic-analysis-agent
python main.py --image your-app:latest
```

### Options

- `--image`: Docker image name to analyze (required)
- `--port`: Port the application runs on (default: 8080)
- `--url`: Custom base URL (default: http://localhost:{port})

### Example

```bash
python main.py --image my-web-app:v1.0 --port 3000
```

The agent will:
1. Start the specified Docker container
2. Perform dynamic security tests including:
   - Basic connectivity and vulnerability checks
   - Port scanning with Nmap
   - Web server scanning with Nikto
   - Comprehensive web app scanning with OWASP ZAP
3. Report any potential vulnerabilities
4. Clean up the container and security tools

## Project Structure

```
dynamic-analysis-agent/
├── main.py                 # Entry point script
├── requirements.txt        # Python dependencies
├── src/                    # Source modules
│   ├── __init__.py
│   ├── docker_manager.py   # Docker container management
│   ├── vulnerability_scanner.py  # Basic vulnerability tests
│   └── tool_integrations.py      # External tool integrations
└── README.md
```

## Extending the Agent

The agent is designed to be modular and extensible:

- **Add new vulnerability tests**: Extend `src/vulnerability_scanner.py`
- **Integrate new tools**: Add functions to `src/tool_integrations.py`
- **Custom Docker setups**: Modify `src/docker_manager.py`
- **New scanning modules**: Create additional files in `src/` and import them in `main.py`

## Disclaimer

This tool performs basic security testing and should not be considered a comprehensive security audit. For thorough security assessment, use professional security tools and services.
