"""
Unit tests for utility functions.
"""

from unittest.mock import patch, MagicMock
import pytest

from src.utils import cleanup


@pytest.mark.unit
class TestUtils:
    """Test cases for utility functions."""

    @patch('src.utils.cleanup_container')
    @patch('src.utils.stop_zap')
    def test_cleanup_success(self, mock_stop_zap, mock_cleanup_container):
        """Test successful cleanup."""
        mock_cleanup_container.return_value = True
        mock_stop_zap.return_value = True

        # Test cleanup with zap process
        mock_zap_process = MagicMock()
        cleanup(container_name="test-container", zap_process=mock_zap_process)

        mock_cleanup_container.assert_called_once_with("test-container")
        mock_stop_zap.assert_called_once_with(mock_zap_process)

    @patch('src.utils.cleanup_container')
    @patch('src.utils.stop_zap')
    def test_cleanup_without_zap_process(self, mock_stop_zap, mock_cleanup_container):
        """Test cleanup without zap process."""
        mock_cleanup_container.return_value = True
        mock_stop_zap.return_value = True

        cleanup(container_name="test-container")

        mock_cleanup_container.assert_called_once_with("test-container")
        mock_stop_zap.assert_called_once_with(None)

    @patch('src.utils.cleanup_container')
    @patch('src.utils.stop_zap')
    def test_cleanup_default_container_name(self, mock_stop_zap, mock_cleanup_container):
        """Test cleanup with default container name."""
        mock_cleanup_container.return_value = True
        mock_stop_zap.return_value = True

        cleanup()

        mock_cleanup_container.assert_called_once_with("test-app")
        mock_stop_zap.assert_called_once_with(None)

    @patch('src.utils.cleanup_container')
    @patch('src.utils.stop_zap')
    def test_cleanup_container_failure(self, mock_stop_zap, mock_cleanup_container):
        """Test cleanup when container cleanup fails."""
        mock_cleanup_container.return_value = False
        mock_stop_zap.return_value = True

        # Should not raise exception, just log the failure
        cleanup(container_name="test-container")

        mock_cleanup_container.assert_called_once_with("test-container")
        mock_stop_zap.assert_called_once_with(None)

    @patch('src.utils.cleanup_container')
    @patch('src.utils.stop_zap')
    def test_cleanup_zap_failure(self, mock_stop_zap, mock_cleanup_container):
        """Test cleanup when zap stop fails."""
        mock_cleanup_container.return_value = True
        mock_stop_zap.return_value = False

        # Should not raise exception
        cleanup(container_name="test-container", zap_process=MagicMock())

        mock_cleanup_container.assert_called_once_with("test-container")
        mock_stop_zap.assert_called_once()
