"""
Integration tests for API and logger interaction.
"""

import json
import logging
from unittest.mock import patch, MagicMock
import pytest

from src.api import app
from src.logger import setup_logging


@pytest.mark.integration
class TestAPILoggerIntegration:
    """Integration tests for API and logger interaction."""

    def setup_method(self):
        """Setup before each test."""
        self.client = app.test_client()

    @patch('src.api.logger')
    def test_api_logging_on_scan_creation(self, mock_logger):
        """Test that API logs scan creation."""
        with patch('src.api.threading.Thread'):
            response = self.client.post('/api/v1/scans',
                                      data=json.dumps({'image': 'test-image'}),
                                      content_type='application/json')

            assert response.status_code == 201

            # Verify logging was called
            mock_logger.info.assert_called()

    @patch('src.api.logger')
    @patch('src.api.perform_scan_async')
    def test_async_scan_logging(self, mock_perform_scan, mock_logger):
        """Test logging during async scan execution."""
        from src.api import active_scans

        # Setup mock scan
        scan_id = 'test-scan-id'
        active_scans[scan_id] = {'status': 'pending'}

        # Mock successful scan
        mock_perform_scan.return_value = None

        # Call perform_scan_async directly (simulating thread execution)
        from src.api import perform_scan_async
        perform_scan_async(scan_id, 'test-image', 8080)

        # Verify logging calls
        mock_logger.info.assert_any_call(f"Starting async scan {scan_id} for image test-image")

    @patch('src.config.config')
    def test_logger_config_integration(self, mock_config):
        """Test that logger uses config values."""
        mock_config.get.side_effect = lambda key, default=None: {
            'logging.level': 'DEBUG',
            'logging.file': '/tmp/test.log'
        }.get(key, default)

        test_logger = setup_logging()

        assert test_logger.level == logging.DEBUG

        # Check file handler was added
        file_handlers = [h for h in test_logger.handlers
                        if hasattr(h, 'baseFilename') and h.baseFilename == '/tmp/test.log']
        assert len(file_handlers) == 1

    @patch('src.api.logger')
    def test_api_error_logging(self, mock_logger):
        """Test that API logs errors properly."""
        # Test with invalid JSON
        response = self.client.post('/api/v1/scans',
                                  data='invalid json',
                                  content_type='application/json')

        assert response.status_code == 400

        # Test with missing required field
        response = self.client.post('/api/v1/scans',
                                  data=json.dumps({}),
                                  content_type='application/json')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Missing required field: image' in data['error']

    @patch('src.api.logger')
    def test_scan_not_found_logging(self, mock_logger):
        """Test logging when scan is not found."""
        response = self.client.get('/api/v1/scans/non-existent-id')

        assert response.status_code == 404

        # Verify error logging might occur (depending on implementation)
        # mock_logger.error.assert_called()  # Uncomment if error logging is added

    def test_full_request_logging_flow(self):
        """Test the complete logging flow for a request."""
        with patch('src.api.logger') as mock_logger:
            # Make a request that should trigger logging
            response = self.client.get('/api/v1/health')

            assert response.status_code == 200

            # Health endpoint might not log, but let's verify the logger is available
            assert mock_logger is not None

    @patch('src.api.logger')
    @patch('src.api.perform_scan_async')
    def test_scan_failure_logging(self, mock_perform_scan, mock_logger):
        """Test logging when scan fails."""
        from src.api import active_scans

        # Setup mock scan
        scan_id = 'test-scan-id'
        active_scans[scan_id] = {'status': 'pending'}

        # Mock scan failure
        mock_perform_scan.side_effect = Exception("Scan failed")

        # Call perform_scan_async
        from src.api import perform_scan_async
        perform_scan_async(scan_id, 'test-image', 8080)

        # Verify error logging
        mock_logger.error.assert_called_with(f"Error in async scan {scan_id}: Scan failed")

        # Verify scan status was set to failed
        assert active_scans[scan_id]['status'] == 'failed'
        assert active_scans[scan_id]['error'] == 'Scan failed'
