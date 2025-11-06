"""
Integration tests for API and configuration interaction.
"""

import json
import tempfile
import os
import yaml
from unittest.mock import patch
import pytest

from src.api import app
from src.config import Config


@pytest.mark.integration
class TestAPIConfigIntegration:
    """Integration tests for API and config interaction."""

    def setup_method(self):
        """Setup before each test."""
        self.client = app.test_client()
        # Create a temporary config for testing
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        self.temp_config_path = self.temp_config.name
        test_config = {
            'docker': {
                'default_container_name': 'integration-test-app',
                'cleanup_after_scan': False
            },
            'scanning': {
                'timeout_per_request': 5
            }
        }
        yaml.dump(test_config, self.temp_config)
        self.temp_config.close()

    def teardown_method(self):
        """Cleanup after each test."""
        if os.path.exists(self.temp_config_path):
            os.unlink(self.temp_config_path)

    @patch('src.config.config')
    def test_api_config_interaction(self, mock_config):
        """Test that API uses config values correctly."""
        # Mock config to return values from our temp file
        mock_config.get.side_effect = lambda key, default=None: {
            'docker.default_container_name': 'integration-test-app',
            'docker.cleanup_after_scan': False,
            'scanning.timeout_per_request': 5
        }.get(key, default)

        # Test config endpoint
        response = self.client.get('/api/v1/config')
        assert response.status_code == 200
        config_data = json.loads(response.data)

        assert config_data['docker']['default_container_name'] == 'integration-test-app'
        assert config_data['scanning']['timeout_per_request'] == 5

    @patch('src.config.config')
    def test_api_scan_creation_with_config(self, mock_config):
        """Test scan creation uses config defaults."""
        mock_config.get.side_effect = lambda key, default=None: {
            'docker.default_port': 9090
        }.get(key, default)

        with patch('src.api.threading.Thread'):
            response = self.client.post('/api/v1/scans',
                                      data=json.dumps({'image': 'test-image'}),
                                      content_type='application/json')

            assert response.status_code == 201
            scan_data = json.loads(response.data)

            # Verify scan was created with config defaults
            from src.api import active_scans
            scan_id = scan_data['scan_id']
            assert active_scans[scan_id]['port'] == 9090

    def test_config_file_loading_integration(self):
        """Test that config file is properly loaded and used."""
        # Create a config instance with our temp file
        config = Config(self.temp_config_path)

        # Verify config was loaded
        assert config.get('docker.default_container_name') == 'integration-test-app'
        assert config.get('docker.cleanup_after_scan') is False
        assert config.get('scanning.timeout_per_request') == 5

        # Test config persistence
        config.set('test.integration_key', 'integration_value')
        config.save_config()

        # Reload config and verify
        new_config = Config(self.temp_config_path)
        assert new_config.get('test.integration_key') == 'integration_value'

    def test_config_api_integration(self):
        """Test full integration between config file, config object, and API."""
        # Load config from file
        config = Config(self.temp_config_path)

        # Modify config programmatically
        config.set('api.test_endpoint', '/test')
        config.set('logging.level', 'DEBUG')

        # Save and reload
        config.save_config()
        reloaded_config = Config(self.temp_config_path)

        # Verify through API (mock the global config)
        with patch('src.api.config', reloaded_config):
            response = self.client.get('/api/v1/config')
            assert response.status_code == 200
            data = json.loads(response.data)

            assert data['docker']['default_container_name'] == 'integration-test-app'
            assert data['scanning']['timeout_per_request'] == 5

    @patch('src.config.config')
    def test_config_defaults_fallback(self, mock_config):
        """Test that API falls back to defaults when config is missing."""
        # Mock config to return None for missing keys
        mock_config.get.return_value = None

        # API should still work with defaults
        response = self.client.post('/api/v1/scans',
                                  data=json.dumps({'image': 'test-image'}),
                                  content_type='application/json')

        # Should succeed even with missing config
        assert response.status_code == 201
