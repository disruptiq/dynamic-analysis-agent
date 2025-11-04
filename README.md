# Dynamic Analysis Agent

A cybersecurity tool for performing dynamic analysis tests on applications running in sandboxed Docker containers.

## Features

- Automated Docker container setup and management
- Basic connectivity testing
- **Comprehensive vulnerability scanning (20+ types)**:
  - **Injection Attacks**: SQL, Command, LDAP, XPath, NoSQL, GraphQL
  - **Template Injection**: SSTI, Template injection detection
  - **Authentication & Authorization**: Broken auth, session management, access control
  - **Data Exposure**: Sensitive data detection, information disclosure
  - **Input Validation**: XSS, CSRF, host header injection, HPP
  - **Protocol Attacks**: XXE, SSRF, HTTP request smuggling
  - **Application Logic**: Race conditions, buffer overflows, format strings
  - **Configuration Issues**: Security misconfigurations, known vulnerabilities
  - **File Handling**: Directory traversal, file upload vulnerabilities
- Integration with industry-standard security tools:
  - OWASP ZAP for comprehensive web application scanning
  - Nmap for port scanning and service enumeration
  - Nikto for web server vulnerability detection
- Flexible reporting:
  - JSON export for programmatic processing
  - HTML reports with charts and detailed analysis
  - PDF reports with professional formatting
  - CSV export for spreadsheet analysis
  - Auto-generated timestamps and organized output
- Advanced configuration and extensibility

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

## Configuration

The agent supports YAML-based configuration for customizing scan behavior. Create a default configuration file:

```bash
python main.py --create-config
```

This will create a `config.yaml` file with all available options. Key configuration sections:

- `docker`: Container management settings
- `tools`: Tool-specific configurations (ZAP, Nmap, Nikto)
- `scanning`: Scan behavior parameters
- `reporting`: Output and reporting options
- `logging`: Logging configuration

Example configuration snippet:
```yaml
tools:
  zap:
    enabled: true
    port: 8090
    timeout: 300
  nmap:
    enabled: true
    timeout: 30

reporting:
  default_format: json
  include_raw_output: true

api:
  host: 0.0.0.0
  port: 5000
  debug: false
```

## REST API

The agent provides a REST API for programmatic access to scanning capabilities.

### Starting the API Server

```bash
# Using main script
python main.py --api --api-port 8080

# Using dedicated API server
python api_server.py --host 127.0.0.1 --port 8080
```

### API Endpoints

#### POST /api/v1/scans
Create a new scan.

**Request Body:**
```json
{
  "image": "my-web-app:latest",
  "port": 8080,
  "url": "http://localhost:8080"
}
```

**Response:**
```json
{
  "scan_id": "uuid-here",
  "status": "pending",
  "message": "Scan started successfully"
}
```

#### GET /api/v1/scans
List all scans.

**Response:**
```json
{
  "scans": [
    {
      "id": "uuid-here",
      "status": "completed",
      "image": "my-web-app:latest",
      "created_at": 1234567890.123,
      "target": "http://localhost:8080"
    }
  ]
}
```

#### GET /api/v1/scans/{scan_id}
Get scan results.

**Response:**
```json
{
  "target": "http://localhost:8080",
  "timestamp": 1234567890.123,
  "vulnerabilities": [...],
  "tools": [...],
  "summary": {...}
}
```

#### DELETE /api/v1/scans/{scan_id}
Delete a scan or cancel if running.

#### GET /api/v1/health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": 1234567890.123,
  "version": "1.0.0"
}
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
- `--output-format`: Output format for results (json or html, default: json)
- `--output-file`: Output file path (default: auto-generated with timestamp)
- `--config`: Path to configuration file (default: auto-detect)
- `--create-config`: Create a default configuration file and exit
- `--api`: Run the API server instead of performing a scan
- `--api-host`: Host for API server (default: 0.0.0.0)
- `--api-port`: Port for API server (default: 5000)

### Examples

Basic scan:
```bash
python main.py --image my-web-app:v1.0 --port 3000
```

Generate HTML report:
```bash
python main.py --image my-web-app:v1.0 --output-format html --output-file security_report.html
```

Custom output location:
```bash
python main.py --image my-web-app:v1.0 --output-format json --output-file ./reports/scan_results.json
```

Create and use custom configuration:
```bash
# Create default config
python main.py --create-config

# Use custom config
python main.py --image my-web-app:v1.0 --config ./my-config.yaml
```

Run API server:
```bash
# Start API server
python main.py --api --api-port 8080

# Or use the dedicated API server script
python api_server.py --port 8080
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
├── main.py                         # Entry point script (CLI + API modes)
├── api_server.py                  # Dedicated API server
├── requirements.txt                # Python dependencies
├── config.yaml                     # Configuration file
├── test/                           # Test applications and environments
│   ├── vulnerable_app.py          # Intentionally vulnerable Flask app
│   ├── Dockerfile                 # Test app containerization
│   ├── docker-compose.yml         # Test environment orchestration
│   └── README.md                  # Test setup instructions
├── src/                           # Source modules
│   ├── __init__.py
│   ├── api.py                     # REST API implementation
│   ├── config.py                  # Configuration management
│   ├── docker_manager.py          # Docker container management
│   ├── logger.py                  # Logging system
│   ├── progress.py                # Progress tracking
│   ├── vulnerability_scanner_main.py  # Vulnerability test orchestrator
│   ├── tools/                     # External tool integrations
│   │   ├── __init__.py
│   │   ├── zap_scanner.py         # OWASP ZAP integration
│   │   ├── nmap_scanner.py        # Nmap integration
│   │   └── nikto_scanner.py       # Nikto integration
│   └── vulnerability_scanner/     # Individual vulnerability scanners
│       ├── __init__.py
│       ├── sql_injection.py       # SQL injection tests
│       ├── command_injection.py   # Command injection tests
│       ├── xxe.py                 # XML external entity tests
│       ├── ssrf.py                # Server-side request forgery
│       ├── csrf.py                # Cross-site request forgery
│       ├── broken_auth.py         # Broken authentication
│       ├── sensitive_data.py      # Sensitive data exposure
│       ├── broken_access.py       # Broken access control
│       ├── security_misconfig.py  # Security misconfigurations
│       ├── known_vulns.py         # Known vulnerabilities
│       ├── insufficient_logging.py # Logging issues
│       ├── race_conditions.py     # Race condition tests
│       ├── buffer_overflow.py     # Buffer overflow tests
│       ├── format_string.py       # Format string vulnerabilities
│       ├── ldap_injection.py      # LDAP injection
│       ├── xpath_injection.py     # XPath injection
│       ├── nosql_injection.py     # NoSQL injection
│       ├── graphql_injection.py   # GraphQL injection
│       ├── template_injection.py  # Template injection
│       ├── ssti.py                # Server-side template injection
│       ├── hpp.py                 # HTTP parameter pollution
│       ├── host_header.py         # Host header injection
│       └── http_smuggling.py      # HTTP request smuggling
└── README.md
```

## Extending the Agent

The agent is designed to be highly modular and extensible:

### Adding New Vulnerability Tests
- Extend `src/vulnerability_scanner.py` with new test functions
- Follow the pattern: `def test_[vulnerability_type](base_url) -> list`

### Integrating New Tools
- Create a new file in `src/tools/` (e.g., `newtool_scanner.py`)
- Implement the scanner function: `def perform_[tool]_scan(...) -> dict`
- Add imports to `src/tools/__init__.py`
- Update `main.py` and `src/api.py` imports

### Custom Docker Setups
- Modify `src/docker_manager.py` for custom container management
- Add new functions for specialized container operations

### New Scanning Modules
- Create additional files in `src/` following the established patterns
- Update imports in `main.py` and relevant API endpoints
- Add configuration options in `config.py` if needed

### API Extensions
- Add new endpoints in `src/api.py`
- Follow RESTful conventions for new resources
- Update API documentation in README.md

## Disclaimer

This tool performs basic security testing and should not be considered a comprehensive security audit. For thorough security assessment, use professional security tools and services.
