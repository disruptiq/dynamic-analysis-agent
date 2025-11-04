"""
Configuration management for the Dynamic Analysis Agent.
"""

import os
import yaml
from typing import Dict, Any

class Config:
    """Configuration manager for the Dynamic Analysis Agent."""

    DEFAULT_CONFIG = {
        "docker": {
            "default_container_name": "test-app",
            "cleanup_after_scan": True
        },
        "tools": {
            "zap": {
                "enabled": True,
                "port": 8090,
                "timeout": 300
            },
            "nmap": {
                "enabled": True,
                "timeout": 30,
                "aggressive_scan": False
            },
            "nikto": {
                "enabled": True,
                "timeout": 60,
                "aggressive_scan": False
            }
        },
        "scanning": {
            "max_payloads_per_test": 10,
            "timeout_per_request": 10,
            "follow_redirects": True,
            "verify_ssl": False
        },
        "reporting": {
            "default_format": "json",
            "include_raw_output": True,
            "max_vulnerabilities_display": 50
        },
        "logging": {
            "level": "INFO",
            "file": "scan.log",
            "max_file_size": 10485760,  # 10MB
            "backup_count": 5
        }
    }

    def __init__(self, config_file: str = None):
        self.config_file = config_file or self._find_config_file()
        self.config = self.DEFAULT_CONFIG.copy()
        self.load_config()

    def _find_config_file(self) -> str:
        """Find configuration file in standard locations."""
        search_paths = [
            os.path.join(os.getcwd(), "config.yaml"),
            os.path.join(os.getcwd(), "config.yml"),
            os.path.join(os.path.dirname(__file__), "..", "config.yaml"),
            os.path.join(os.path.expanduser("~"), ".dynamic-analysis-agent", "config.yaml")
        ]

        for path in search_paths:
            if os.path.isfile(path):
                return path

        return os.path.join(os.getcwd(), "config.yaml")

    def load_config(self):
        """Load configuration from file."""
        if os.path.isfile(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    user_config = yaml.safe_load(f)
                self._merge_config(self.config, user_config)
                print(f"Loaded configuration from {self.config_file}")
            except Exception as e:
                print(f"Error loading config file {self.config_file}: {e}")
        else:
            print("No configuration file found, using defaults")

    def _merge_config(self, base: Dict[str, Any], update: Dict[str, Any]):
        """Recursively merge configuration dictionaries."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value

    def save_config(self, file_path: str = None):
        """Save current configuration to file."""
        save_path = file_path or self.config_file
        dir_path = os.path.dirname(save_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

        try:
            with open(save_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, indent=2)
            print(f"Configuration saved to {save_path}")
        except Exception as e:
            print(f"Error saving config to {save_path}: {e}")

    def get(self, key: str, default=None):
        """Get configuration value by dot-separated key."""
        keys = key.split('.')
        value = self.config

        try:
            for k in keys:
                value = value[k]
            return value
        except KeyError:
            return default

    def set(self, key: str, value: Any):
        """Set configuration value by dot-separated key."""
        keys = key.split('.')
        config = self.config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def create_default_config(self, file_path: str = None):
        """Create a default configuration file."""
        save_path = file_path or "config.yaml"
        self.save_config(save_path)
        print(f"Created default configuration file at {save_path}")

    def __getitem__(self, key: str):
        return self.get(key)

    def __setitem__(self, key: str, value: Any):
        self.set(key, value)

# Global configuration instance
config = Config()
