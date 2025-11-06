"""
Unit tests for configuration management.
"""

import os
import tempfile
import pytest
import yaml
from unittest.mock import patch, mock_open

from src.config import Config


@pytest.mark.unit
class TestConfig:
    """Test cases for Config class."""

    def test_default_config_initialization(self):
        """Test that Config initializes with default values."""
        config = Config()
        assert config.config is not None
        assert 'docker' in config.config
        assert 'tools' in config.config
        assert 'scanning' in config.config
        assert 'reporting' in config.config
        assert 'logging' in config.config

    def test_get_method(self):
        """Test getting configuration values."""
        config = Config()

        # Test getting existing values
        assert config.get('docker.default_container_name') == 'test-app'
        assert config.get('tools.zap.enabled') is True
        assert config.get('logging.level') == 'INFO'

        # Test getting non-existent values with default
        assert config.get('non.existent.key', 'default_value') == 'default_value'

        # Test getting non-existent values without default
        assert config.get('non.existent.key') is None

    def test_set_method(self):
        """Test setting configuration values."""
        config = Config()

        # Test setting new values
        config.set('custom.new_key', 'test_value')
        assert config.get('custom.new_key') == 'test_value'

        # Test setting nested values
        config.set('custom.nested.deep', 42)
        assert config.get('custom.nested.deep') == 42

        # Test overwriting existing values
        config.set('docker.default_container_name', 'modified-app')
        assert config.get('docker.default_container_name') == 'modified-app'

    def test_config_file_loading(self):
        """Test loading configuration from file."""
        # Create a temporary config file
        test_config = {
            'docker': {
                'default_container_name': 'test-container',
                'cleanup_after_scan': False
            },
            'logging': {
                'level': 'DEBUG'
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(test_config, f)
            temp_config_file = f.name

        try:
            config = Config(temp_config_file)

            # Test that custom config was loaded
            assert config.get('docker.default_container_name') == 'test-container'
            assert config.get('docker.cleanup_after_scan') is False
            assert config.get('logging.level') == 'DEBUG'

            # Test that other defaults are preserved
            assert config.get('tools.zap.enabled') is True

        finally:
            os.unlink(temp_config_file)

    def test_config_file_not_found(self):
        """Test behavior when config file doesn't exist."""
        # Use a path that definitely doesn't exist
        import tempfile
        non_existent_path = os.path.join(tempfile.gettempdir(), 'definitely_non_existent_config.yaml')

        config = Config(non_existent_path)

        # Should use default config - check that docker section exists
        assert 'docker' in config.config
        assert 'default_container_name' in config.config['docker']
        assert config.config_file == non_existent_path

    def test_save_config(self):
        """Test saving configuration to file."""
        config = Config()
        config.set('test.key', 'test_value')

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_file = f.name

        try:
            config.save_config(temp_file)

            # Verify file was created and contains expected content
            with open(temp_file, 'r') as f:
                saved_config = yaml.safe_load(f)

            assert saved_config['test']['key'] == 'test_value'

        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_merge_config(self):
        """Test configuration merging."""
        config = Config()

        base = {
            'a': 1,
            'b': {'c': 2, 'd': 3},
            'e': [1, 2, 3]
        }

        update = {
            'b': {'c': 20, 'f': 4},
            'g': 5
        }

        config._merge_config(base, update)

        assert base['a'] == 1
        assert base['b']['c'] == 20  # Overwritten
        assert base['b']['d'] == 3   # Preserved
        assert base['b']['f'] == 4   # Added
        assert base['g'] == 5        # Added
        assert base['e'] == [1, 2, 3]  # Preserved

    def test_getitem_setitem(self):
        """Test dictionary-like access."""
        config = Config()

        # Test __setitem__
        config['test.item'] = 'value'
        assert config['test.item'] == 'value'

        # Test __getitem__ - check that it returns a value
        docker_name = config['docker.default_container_name']
        assert docker_name is not None
        assert isinstance(docker_name, str)

    def test_find_config_file(self):
        """Test config file discovery."""
        config = Config()

        # Test with different search paths
        search_paths = [
            os.path.join(os.getcwd(), "config.yaml"),
            os.path.join(os.getcwd(), "config.yml"),
            os.path.join(os.path.dirname(__file__), "..", "config.yaml"),
        ]

        # Create a temporary config in current directory
        temp_config = os.path.join(os.getcwd(), "config.yaml")
        try:
            with open(temp_config, 'w') as f:
                yaml.dump({'test': 'value'}, f)

            found_path = config._find_config_file()
            assert found_path == temp_config

        finally:
            if os.path.exists(temp_config):
                os.unlink(temp_config)

    @patch('os.path.isfile')
    def test_find_config_file_no_file(self, mock_isfile):
        """Test config file discovery when no file exists."""
        mock_isfile.return_value = False

        config = Config()
        found_path = config._find_config_file()

        expected_path = os.path.join(os.getcwd(), "config.yaml")
        assert found_path == expected_path
