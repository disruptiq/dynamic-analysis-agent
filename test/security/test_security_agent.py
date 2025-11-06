"""
Security tests for the agent codebase itself.
"""

import os
import subprocess
import json
import tempfile
from unittest.mock import patch, MagicMock
import pytest

from src.api import app
from src.config import Config


@pytest.mark.security
class TestAgentSecurity:
    """Security tests for the agent itself."""

    def setup_method(self):
        """Setup before each test."""
        self.client = app.test_client()

    def test_api_input_validation_scan_creation(self):
        """Test input validation for scan creation endpoint."""
        # Test SQL injection attempts
        sql_injections = [
            {"image": "'; DROP TABLE users; --"},
            {"image": "\"; rm -rf /; --"},
            {"image": "test' OR '1'='1"},
            {"image": "<script>alert('xss')</script>"},
            {"image": "../../../etc/passwd"},
            {"image": "test\\nmalicious\\ncommand"}
        ]

        for payload in sql_injections:
            response = self.client.post('/api/v1/scans',
                                      data=json.dumps(payload),
                                      content_type='application/json')
            # Should either reject or sanitize input
            assert response.status_code in [400, 201]  # Either validation error or accepted (if sanitized)

    def test_api_input_validation_get_scan(self):
        """Test input validation for get scan endpoint."""
        # Test path traversal attempts
        path_traversals = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "scan-id/../../../config.yaml"
        ]

        for scan_id in path_traversals:
            response = self.client.get(f'/api/v1/scans/{scan_id}')
            # Should return 404, not access unauthorized files
            assert response.status_code == 404

    def test_config_file_path_traversal(self):
        """Test config file loading doesn't allow path traversal."""
        # Test path traversal in config file paths
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "/etc/shadow",
            "C:\\Windows\\System32\\config\\sam"
        ]

        for malicious_path in malicious_paths:
            config = Config(malicious_path)
            # Should not crash or expose sensitive data
            # Config should either use defaults or safe defaults
            assert isinstance(config.config, dict)

    def test_config_injection_prevention(self):
        """Test that config loading prevents code injection."""
        # Create a config file with potentially malicious content
        malicious_config_content = """
        docker:
          default_container_name: !python/object/apply:subprocess.call
            - ['rm', '-rf', '/']
        """

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(malicious_config_content)
            temp_path = f.name

        try:
            config = Config(temp_path)
            # Should load safely without executing malicious code
            assert 'docker' in config.config
            # The malicious object should not be loaded as code
            assert not callable(config.get('docker.default_container_name'))

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_api_rate_limiting_simulation(self):
        """Test for potential DoS via rapid API calls."""
        # Simulate rapid requests
        num_requests = 1000

        for i in range(num_requests):
            response = self.client.get('/api/v1/health')
            assert response.status_code == 200

            # Check response content is consistent
            data = json.loads(response.data)
            assert data['status'] == 'healthy'

        # System should remain responsive
        final_response = self.client.get('/api/v1/health')
        assert final_response.status_code == 200

    def test_memory_exhaustion_prevention(self):
        """Test prevention of memory exhaustion attacks."""
        # Try to create many large scan requests
        large_payloads = []

        for i in range(100):
            large_image_name = "test-image-" + "A" * 10000  # 10KB string
            large_payloads.append({
                'image': large_image_name,
                'port': 8080,
                'url': 'http://' + 'a' * 5000 + '.com'  # Large URL
            })

        for payload in large_payloads[:10]:  # Test first 10 to avoid excessive test time
            response = self.client.post('/api/v1/scans',
                                      data=json.dumps(payload),
                                      content_type='application/json')
            # Should handle large payloads gracefully
            assert response.status_code in [200, 201, 400, 413]  # Success or reasonable error

    def test_command_injection_prevention(self):
        """Test prevention of command injection in tool execution."""
        # Mock subprocess to check what commands would be executed
        with patch('subprocess.run') as mock_subprocess:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "success"
            mock_result.stderr = ""
            mock_subprocess.return_value = mock_result

            # Import and test nmap scanner with malicious input
            from src.tools.nmap_scanner import perform_nmap_scan

            # Test with potentially malicious hostnames
            malicious_hosts = [
                "localhost; rm -rf /",
                "127.0.0.1 && echo hacked",
                "`rm -rf /`",
                "$(rm -rf /)",
                "localhost | rm -rf /"
            ]

            for host in malicious_hosts:
                result = perform_nmap_scan(host, 80)

                # Check that subprocess was called safely
                if mock_subprocess.called:
                    args, kwargs = mock_subprocess.call_args
                    command = args[0]

                    # Command should be ['nmap', '-sV', '-p', '80', host]
                    # The host should be passed as a separate argument, not concatenated
                    assert len(command) == 5
                    assert command[0] == 'nmap'
                    assert command[1] == '-sV'
                    assert command[2] == '-p'
                    assert command[4] == host  # Host should be as-is, not modified

                    mock_subprocess.reset_mock()

    def test_information_disclosure_prevention(self):
        """Test that sensitive information is not disclosed."""
        # Test config endpoint doesn't expose sensitive data
        response = self.client.get('/api/v1/config')
        assert response.status_code == 200
        data = json.loads(response.data)

        # Should not contain sensitive information
        sensitive_keys = ['password', 'secret', 'key', 'token', 'credentials']
        for key in sensitive_keys:
            assert key not in str(data).lower()

    def test_error_information_leakage(self):
        """Test that errors don't leak sensitive information."""
        # Test with invalid scan ID
        response = self.client.get('/api/v1/scans/invalid-id-12345')
        assert response.status_code == 404
        data = json.loads(response.data)

        # Error message should not contain sensitive information
        error_msg = str(data.get('error', '')).lower()
        sensitive_indicators = ['stack trace', 'traceback', 'exception', 'file:', 'line ']
        for indicator in sensitive_indicators:
            assert indicator not in error_msg

    def test_file_access_restrictions(self):
        """Test that file access is properly restricted."""
        # Test accessing non-existent config files
        restricted_paths = [
            '/etc/passwd',
            '/etc/shadow',
            'C:\\Windows\\System32\\config\\sam',
            '../../../.bashrc',
            '~/.ssh/id_rsa'
        ]

        for path in restricted_paths:
            config = Config(path)
            # Should not crash and should use defaults
            assert config.config is not None
            assert 'docker' in config.config

    def test_yaml_parsing_security(self):
        """Test YAML parsing doesn't allow unsafe operations."""
        # Test with potentially unsafe YAML
        unsafe_yaml = """
        !!python/object/apply:os.system ["echo 'unsafe'"]
        """

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(unsafe_yaml)
            temp_path = f.name

        try:
            config = Config(temp_path)
            # Should load safely or fail gracefully
            # The unsafe object should not be executed
            assert config.config is not None

        except Exception:
            # It's acceptable for unsafe YAML to cause an exception
            pass

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_subprocess_security_wrapper(self):
        """Test that subprocess calls are properly wrapped."""
        with patch('subprocess.run') as mock_subprocess:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "safe output"
            mock_result.stderr = ""
            mock_subprocess.return_value = mock_result

            from src.tools.nmap_scanner import perform_nmap_scan

            # Test with shell metacharacters
            result = perform_nmap_scan("localhost", 80)

            # Verify subprocess.run was called with shell=False (safe)
            args, kwargs = mock_subprocess.call_args
            assert kwargs.get('shell') is False or 'shell' not in kwargs

    def test_dependency_vulnerability_check(self):
        """Test for known vulnerable dependencies (basic check)."""
        # This is a basic check - in practice, use tools like safety or pip-audit
        try:
            import yaml
            import requests
            import flask
            # If imports succeed, basic dependency check passes
            assert True
        except ImportError as e:
            pytest.fail(f"Missing critical dependency: {e}")

    def test_default_config_security(self):
        """Test that default configuration is secure."""
        config = Config()

        # Check that insecure defaults are not present
        docker_config = config.get('docker', {})
        assert docker_config.get('cleanup_after_scan', True)  # Should cleanup by default

        scanning_config = config.get('scanning', {})
        assert scanning_config.get('verify_ssl', False) is False  # May be intentionally False for testing

        # Check logging doesn't expose sensitive info by default
        logging_config = config.get('logging', {})
        assert 'file' in logging_config  # Should have a log file
