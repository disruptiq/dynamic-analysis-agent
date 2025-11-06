"""
Unit tests for Nmap scanner integration.
"""

import subprocess
import time
from unittest.mock import patch, MagicMock
import pytest

from src.tools.nmap_scanner import perform_nmap_scan


@pytest.mark.unit
class TestNmapScanner:
    """Test cases for Nmap scanner."""

    @patch('subprocess.run')
    def test_perform_nmap_scan_success_single_port(self, mock_subprocess):
        """Test successful nmap scan with single port."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Nmap scan report for localhost (127.0.0.1)\\nHost is up (0.00020s latency).\\nPORT   STATE SERVICE VERSION\\n80/tcp open  http    Apache httpd 2.4.41"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        result = perform_nmap_scan("localhost", 80)

        assert result is not None
        assert result["success"] is True
        assert "output" in result
        assert result["output"] == mock_result.stdout
        assert "timestamp" in result

        # Check subprocess was called correctly
        mock_subprocess.assert_called_once_with(
            ['nmap', '-sV', '-p', '80', 'localhost'],
            capture_output=True,
            text=True,
            timeout=30
        )

    @patch('subprocess.run')
    def test_perform_nmap_scan_success_multiple_ports(self, mock_subprocess):
        """Test successful nmap scan with multiple ports."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Scan results for multiple ports"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        ports = [80, 443, 8080]
        result = perform_nmap_scan("localhost", ports)

        assert result is not None
        assert result["success"] is True

        # Check port string formatting
        mock_subprocess.assert_called_once_with(
            ['nmap', '-sV', '-p', '80,443,8080', 'localhost'],
            capture_output=True,
            text=True,
            timeout=30
        )

    @patch('subprocess.run')
    def test_perform_nmap_scan_failure(self, mock_subprocess):
        """Test nmap scan failure."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Failed to resolve hostname"
        mock_subprocess.return_value = mock_result

        result = perform_nmap_scan("invalid-host", 80)

        assert result is not None
        assert result["success"] is False
        assert result["error"] == "Failed to resolve hostname"
        assert "timestamp" in result

    @patch('subprocess.run')
    def test_perform_nmap_scan_file_not_found(self, mock_subprocess):
        """Test nmap scan when nmap is not installed."""
        mock_subprocess.side_effect = FileNotFoundError("No such file or directory: 'nmap'")

        result = perform_nmap_scan("localhost", 80)

        assert result is None

    @patch('subprocess.run')
    def test_perform_nmap_scan_timeout(self, mock_subprocess):
        """Test nmap scan timeout."""
        mock_subprocess.side_effect = subprocess.TimeoutExpired(
            cmd=['nmap', '-sV', '-p', '80', 'localhost'],
            timeout=30
        )

        result = perform_nmap_scan("localhost", 80)

        assert result is not None
        assert result["success"] is False
        assert result["error"] == "Timeout"
        assert "timestamp" in result

    @patch('subprocess.run')
    def test_perform_nmap_scan_generic_exception(self, mock_subprocess):
        """Test nmap scan with generic exception."""
        mock_subprocess.side_effect = Exception("Network error")

        result = perform_nmap_scan("localhost", 80)

        assert result is not None
        assert result["success"] is False
        assert result["error"] == "Network error"
        assert "timestamp" in result

    def test_perform_nmap_scan_port_conversion(self):
        """Test port parameter conversion."""
        with patch('subprocess.run') as mock_subprocess:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "success"
            mock_result.stderr = ""
            mock_subprocess.return_value = mock_result

            # Test string port conversion
            perform_nmap_scan("localhost", "80")
            args, kwargs = mock_subprocess.call_args
            assert args[0][3] == '80'  # port string

            # Test integer port
            perform_nmap_scan("localhost", 80)
            args, kwargs = mock_subprocess.call_args
            assert args[0][3] == '80'

            # Test list of integers
            perform_nmap_scan("localhost", [80, 443])
            args, kwargs = mock_subprocess.call_args
            assert args[0][3] == '80,443'

            # Test list of strings
            perform_nmap_scan("localhost", ["80", "443"])
            args, kwargs = mock_subprocess.call_args
            assert args[0][3] == '80,443'

    @patch('subprocess.run')
    def test_perform_nmap_scan_output_structure(self, mock_subprocess):
        """Test the structure of successful scan output."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Detailed nmap output here"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        start_time = time.time()
        result = perform_nmap_scan("localhost", 80)

        assert result["success"] is True
        assert result["output"] == "Detailed nmap output here"
        assert isinstance(result["timestamp"], float)
        assert result["timestamp"] >= start_time
        assert result["timestamp"] <= time.time()
