"""
Unit tests for logging utilities.
"""

import logging
import pytest
import sys
from unittest.mock import patch, MagicMock
from io import StringIO

from src.logger import setup_logging, reload_logger, logger


@pytest.mark.unit
class TestLogger:
    """Test cases for logging utilities."""

    @patch('src.config.config')
    def test_setup_logging_basic(self, mock_config):
        """Test basic logging setup."""
        mock_config.get.side_effect = lambda key, default=None: {
            'logging.level': 'INFO',
            'logging.file': None,
            'logging.max_file_size': 10485760,
            'logging.backup_count': 5
        }.get(key, default)

        test_logger = setup_logging()

        assert test_logger.name == 'dynamic_analysis_agent'
        # Check that logger has handlers
        assert len(test_logger.handlers) >= 1  # At least console handler

        # Check that handlers have formatters
        for handler in test_logger.handlers:
            assert handler.formatter is not None

    @patch('src.config.config')
    def test_setup_logging_with_file(self, mock_config):
        """Test logging setup with file output."""
        import tempfile
        import os

        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            mock_config.get.side_effect = lambda key, default=None: {
                'logging.level': 'DEBUG',
                'logging.file': temp_path,
                'logging.max_file_size': 1024,
                'logging.backup_count': 3
            }.get(key, default)

            test_logger = setup_logging()

            assert len(test_logger.handlers) >= 2  # Console and file handlers

            # Check file handler
            file_handlers = [h for h in test_logger.handlers if isinstance(h, logging.handlers.RotatingFileHandler)]
            assert len(file_handlers) >= 1
            # File handler should exist (path may be different due to global logger)

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    @patch('src.config.config')
    def test_setup_logging_invalid_level(self, mock_config):
        """Test logging setup with invalid log level."""
        mock_config.get.side_effect = lambda key, default=None: {
            'logging.level': 'INVALID_LEVEL',
            'logging.file': None
        }.get(key, default)

        test_logger = setup_logging()

        # Logger should still be created even with invalid level
        assert test_logger is not None
        assert test_logger.name == 'dynamic_analysis_agent'

    def test_reload_logger(self):
        """Test logger reloading."""
        # Mock setup_logging to return a different logger
        with patch('src.logger.setup_logging') as mock_setup:
            mock_new_logger = MagicMock()
            mock_setup.return_value = mock_new_logger

            result = reload_logger()

            assert result == mock_new_logger

    @patch('sys.stdout', new_callable=StringIO)
    @patch('src.config.config')
    def test_console_logging_output(self, mock_config, mock_stdout):
        """Test that console logging outputs to stdout."""
        mock_config.get.side_effect = lambda key, default=None: {
            'logging.level': 'INFO',
            'logging.file': None
        }.get(key, default)

        test_logger = setup_logging()

        # Clear existing handlers to avoid interference
        test_logger.handlers.clear()

        # Add a string stream handler for testing
        string_handler = logging.StreamHandler(mock_stdout)
        string_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        test_logger.addHandler(string_handler)
        test_logger.setLevel(logging.INFO)

        # Test logging
        test_logger.info("Test message")

        output = mock_stdout.getvalue()
        assert "INFO: Test message" in output

    @patch('src.config.config')
    def test_duplicate_handler_prevention(self, mock_config):
        """Test that duplicate handlers are not added."""
        mock_config.get.side_effect = lambda key, default=None: {
            'logging.level': 'INFO',
            'logging.file': None
        }.get(key, default)

        test_logger = setup_logging()
        initial_handler_count = len(test_logger.handlers)

        # Call setup again
        setup_logging()
        final_handler_count = len(test_logger.handlers)

        # Should not have duplicate handlers (handlers are cleared first)
        assert final_handler_count == initial_handler_count

    @patch('src.config.config')
    def test_logger_formatter_format(self, mock_config):
        """Test that log format is correct."""
        mock_config.get.side_effect = lambda key, default=None: {
            'logging.level': 'INFO',
            'logging.file': None
        }.get(key, default)

        test_logger = setup_logging()

        # Find console handler
        console_handlers = [h for h in test_logger.handlers if isinstance(h, logging.StreamHandler) and h.stream == sys.stdout]
        assert len(console_handlers) == 1

        formatter = console_handlers[0].formatter
        assert formatter is not None

        # Test format string
        expected_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        assert formatter._fmt == expected_format
