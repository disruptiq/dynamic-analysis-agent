"""
Pytest configuration and shared fixtures for testing.
"""

import pytest
import tempfile
import os
import yaml
from unittest.mock import patch

from src.api import app, active_scans, scan_results
from src.config import Config


@pytest.fixture(scope='session')
def temp_config_file():
    """Create a temporary config file for testing."""
    config_data = {
        'docker': {
            'default_container_name': 'test-app',
            'cleanup_after_scan': True
        },
        'tools': {
            'zap': {
                'enabled': True,
                'port': 8090,
                'timeout': 300
            }
        },
        'scanning': {
            'max_payloads_per_test': 10,
            'timeout_per_request': 10
        }
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config_data, f)
        temp_path = f.name

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def api_client():
    """API test client fixture."""
    with app.test_client() as client:
        yield client


@pytest.fixture
def clean_scan_state():
    """Ensure clean scan state for each test."""
    initial_active = active_scans.copy()
    initial_results = scan_results.copy()

    active_scans.clear()
    scan_results.clear()

    yield

    # Restore initial state
    active_scans.clear()
    active_scans.update(initial_active)
    scan_results.clear()
    scan_results.update(initial_results)


@pytest.fixture
def mock_config():
    """Mock config for testing."""
    with patch('src.config.config') as mock_config:
        mock_config.get.side_effect = lambda key, default=None: {
            'docker.default_container_name': 'test-app',
            'docker.cleanup_after_scan': True,
            'tools.zap.enabled': True,
            'tools.zap.port': 8090,
            'logging.level': 'INFO',
            'scanning.timeout_per_request': 10
        }.get(key, default)
        mock_config.set = lambda key, value: None
        yield mock_config


@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    with patch('src.logger.logger') as mock_logger:
        yield mock_logger


@pytest.fixture
def mock_subprocess():
    """Mock subprocess for testing external commands."""
    with patch('subprocess.run') as mock_run:
        mock_result = type('MockResult', (), {
            'returncode': 0,
            'stdout': 'success',
            'stderr': ''
        })()
        mock_run.return_value = mock_result
        yield mock_run


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances between tests."""
    # This helps ensure test isolation
    from src import config
    from src import logger

    # Force reload of singletons if needed
    # (In this case, they're already mocked or isolated)


# Custom markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "load: Load tests")
    config.addinivalue_line("markers", "security: Security tests")


# Test data fixtures
@pytest.fixture
def sample_scan_data():
    """Sample scan data for testing."""
    return {
        'image': 'test-app',
        'port': 8080,
        'url': 'http://localhost:8080'
    }


@pytest.fixture
def sample_vulnerability():
    """Sample vulnerability data."""
    return {
        'type': 'xss',
        'severity': 'high',
        'description': 'Cross-site scripting vulnerability',
        'url': 'http://localhost:8080/vulnerable',
        'payload': '<script>alert("xss")</script>'
    }


@pytest.fixture
def sample_tool_result():
    """Sample tool result data."""
    return {
        'name': 'nmap',
        'results': {
            'open_ports': [80, 443],
            'services': ['http', 'https']
        },
        'success': True
    }
