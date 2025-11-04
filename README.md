# Dynamic Analysis Agent

A cybersecurity tool for performing dynamic analysis tests on applications running in sandboxed Docker containers.

## Features

- Automated Docker container setup and management
- Basic connectivity testing
- Vulnerability scanning for common web security issues:
  - SQL Injection
  - Cross-Site Scripting (XSS)
  - Directory Traversal

## Installation

1. Ensure Docker is installed and running on your system.
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the analysis agent with a Docker image:

```bash
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
2. Perform dynamic security tests
3. Report any potential vulnerabilities
4. Clean up the container

## Extending the Agent

The agent is designed to be extensible. Add new test functions to the `test_vulnerabilities()` function or create separate modules for specialized testing.

## Disclaimer

This tool performs basic security testing and should not be considered a comprehensive security audit. For thorough security assessment, use professional security tools and services.
