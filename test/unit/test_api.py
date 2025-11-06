"""
Unit tests for API endpoints.
"""

import json
import time
import uuid
from unittest.mock import patch, MagicMock, call
import pytest
from flask import Flask

from src.api import app, active_scans, scan_results, perform_scan_async


@pytest.mark.unit
class TestAPI:
    """Test cases for API endpoints."""

    def setup_method(self):
        """Setup before each test."""
        # Clear global state
        active_scans.clear()
        scan_results.clear()
        self.client = app.test_client()

    def teardown_method(self):
        """Cleanup after each test."""
        active_scans.clear()
        scan_results.clear()

    @patch('src.api.config')
    def test_create_scan_success(self, mock_config):
        """Test successful scan creation."""
        mock_config.get.return_value = 8080

        with patch('src.api.threading.Thread') as mock_thread:
            mock_thread_instance = MagicMock()
            mock_thread.return_value = mock_thread_instance

            response = self.client.post('/api/v1/scans',
                                      data=json.dumps({'image': 'test-image'}),
                                      content_type='application/json')

            assert response.status_code == 201
            data = json.loads(response.data)

            assert 'scan_id' in data
            assert data['status'] == 'pending'
            assert data['message'] == 'Scan started successfully'

            # Check that scan was added to active_scans
            scan_id = data['scan_id']
            assert scan_id in active_scans
            assert active_scans[scan_id]['image'] == 'test-image'
            assert active_scans[scan_id]['status'] == 'pending'

            # Check that thread was started
            mock_thread.assert_called_once()
            call_kwargs = mock_thread.call_args[1]  # Get kwargs
            assert call_kwargs['target'] == perform_scan_async
            assert call_kwargs['args'] == (scan_id, 'test-image', 8080, None)

    def test_create_scan_missing_image(self):
        """Test scan creation with missing image."""
        response = self.client.post('/api/v1/scans',
                                  data=json.dumps({}),
                                  content_type='application/json')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Missing required field: image' in data['error']

    @patch('src.api.config')
    def test_create_scan_with_custom_port_and_url(self, mock_config):
        """Test scan creation with custom port and URL."""
        mock_config.get.return_value = 8080

        with patch('src.api.threading.Thread'):
            response = self.client.post('/api/v1/scans',
                                      data=json.dumps({
                                          'image': 'test-image',
                                          'port': 9090,
                                          'url': 'http://custom-url.com'
                                      }),
                                      content_type='application/json')

            assert response.status_code == 201
            data = json.loads(response.data)

            scan_id = data['scan_id']
            assert active_scans[scan_id]['port'] == 9090
            assert active_scans[scan_id]['url'] == 'http://custom-url.com'

    def test_list_scans_empty(self):
        """Test listing scans when none exist."""
        response = self.client.get('/api/v1/scans')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['scans'] == []

    def test_list_scans_with_active_and_completed(self):
        """Test listing scans with both active and completed scans."""
        # Add active scan
        active_scan_id = str(uuid.uuid4())
        active_scans[active_scan_id] = {
            'id': active_scan_id,
            'image': 'active-image',
            'status': 'running',
            'created_at': time.time()
        }

        # Add completed scan
        completed_scan_id = str(uuid.uuid4())
        scan_results[completed_scan_id] = {
            'id': completed_scan_id,
            'target': 'http://localhost:8080',
            'status': 'completed',
            'timestamp': time.time(),
            'vulnerabilities': [],
            'tools': [],
            'summary': {}
        }

        response = self.client.get('/api/v1/scans')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['scans']) == 2

        # Check active scan
        active_scan_data = next(s for s in data['scans'] if s['id'] == active_scan_id)
        assert active_scan_data['status'] == 'running'
        assert active_scan_data['image'] == 'active-image'

        # Check completed scan
        completed_scan_data = next(s for s in data['scans'] if s['id'] == completed_scan_id)
        assert completed_scan_data['status'] == 'completed'
        assert completed_scan_data['target'] == 'http://localhost:8080'

    def test_get_scan_active(self):
        """Test getting details of an active scan."""
        scan_id = str(uuid.uuid4())
        active_scans[scan_id] = {
            'id': scan_id,
            'image': 'test-image',
            'status': 'running',
            'created_at': time.time(),
            'port': 8080
        }

        response = self.client.get(f'/api/v1/scans/{scan_id}')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == scan_id
        assert data['status'] == 'running'
        assert data['image'] == 'test-image'

    def test_get_scan_completed(self):
        """Test getting details of a completed scan."""
        scan_id = str(uuid.uuid4())
        scan_results[scan_id] = {
            'id': scan_id,
            'target': 'http://localhost:8080',
            'status': 'completed',
            'timestamp': time.time(),
            'vulnerabilities': [{'type': 'test', 'severity': 'high'}],
            'tools': [{'name': 'nmap', 'results': {}}],
            'summary': {'total_vulnerabilities': 1}
        }

        response = self.client.get(f'/api/v1/scans/{scan_id}')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['target'] == 'http://localhost:8080'
        assert data['vulnerabilities'][0]['type'] == 'test'

    def test_get_scan_not_found(self):
        """Test getting a non-existent scan."""
        response = self.client.get('/api/v1/scans/non-existent-id')

        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Scan not found' in data['error']

    def test_delete_scan_completed(self):
        """Test deleting a completed scan."""
        scan_id = str(uuid.uuid4())
        scan_results[scan_id] = {'id': scan_id, 'status': 'completed'}

        response = self.client.delete(f'/api/v1/scans/{scan_id}')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data
        assert 'Scan deleted successfully' in data['message']

        # Check scan was removed
        assert scan_id not in scan_results

    def test_delete_scan_active(self):
        """Test deleting an active scan."""
        scan_id = str(uuid.uuid4())
        active_scans[scan_id] = {
            'id': scan_id,
            'status': 'running',
            'created_at': time.time()
        }

        response = self.client.delete(f'/api/v1/scans/{scan_id}')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data
        assert 'Scan cancelled' in data['message']

        # Check scan status was changed
        assert active_scans[scan_id]['status'] == 'cancelled'

    def test_delete_scan_not_found(self):
        """Test deleting a non-existent scan."""
        response = self.client.delete('/api/v1/scans/non-existent-id')

        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Scan not found' in data['error']

    def test_health_check(self):
        """Test health check endpoint."""
        response = self.client.get('/api/v1/health')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert data['version'] == '1.0.0'

    @patch('src.api.config')
    def test_get_config(self, mock_config):
        """Test getting configuration."""
        mock_config.get.side_effect = lambda key, default=None: {
            'docker': {'default_container_name': 'test-app'},
            'reporting': {'default_format': 'json'},
            'scanning': {'timeout_per_request': 10}
        }.get(key, {})

        response = self.client.get('/api/v1/config')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['docker']['default_container_name'] == 'test-app'
        assert data['reporting']['default_format'] == 'json'
        assert data['scanning']['timeout_per_request'] == 10

    @patch('src.api.start_zap')
    @patch('src.api.run_docker_container')
    @patch('src.api.test_vulnerabilities')
    @patch('src.api.perform_nmap_scan')
    @patch('src.api.perform_nikto_scan')
    @patch('src.api.perform_zap_scan')
    @patch('src.api.cleanup_container')
    @patch('src.api.stop_zap')
    def test_perform_scan_async_success(self, mock_stop_zap, mock_cleanup,
                                       mock_zap_scan, mock_nikto_scan, mock_nmap_scan,
                                       mock_test_vuln, mock_run_container, mock_start_zap):
        """Test successful async scan execution."""
        # Setup mocks
        mock_start_zap.return_value = MagicMock()
        mock_run_container.return_value = True
        mock_test_vuln.return_value = [{'type': 'xss', 'severity': 'high'}]
        mock_nmap_scan.return_value = {'ports': [8080]}
        mock_nikto_scan.return_value = {'vulnerabilities': []}
        mock_zap_scan.return_value = {'alerts': []}
        mock_cleanup.return_value = True
        mock_stop_zap.return_value = True

        scan_id = str(uuid.uuid4())
        active_scans[scan_id] = {'status': 'pending'}

        # Run async scan
        perform_scan_async(scan_id, 'test-image', 8080)

        # Check that mocks were called
        mock_start_zap.assert_called_once()
        mock_run_container.assert_called_once()
        mock_test_vuln.assert_called_once()
        mock_nmap_scan.assert_called_once()
        mock_nikto_scan.assert_called_once()
        mock_zap_scan.assert_called_once()
        mock_cleanup.assert_called_once()
        mock_stop_zap.assert_called_once()

        # Check results were stored (basic check)
        assert scan_id in scan_results or active_scans[scan_id]['status'] == 'completed'

    @patch('src.api.start_zap')
    @patch('src.api.run_docker_container')
    def test_perform_scan_async_container_failure(self, mock_run_container, mock_start_zap):
        """Test async scan when container fails to start."""
        mock_start_zap.return_value = MagicMock()
        mock_run_container.return_value = False

        scan_id = str(uuid.uuid4())
        active_scans[scan_id] = {'status': 'pending'}

        perform_scan_async(scan_id, 'test-image', 8080)

        assert active_scans[scan_id]['status'] == 'failed'
        assert 'Failed to start container' in active_scans[scan_id]['error']
        assert scan_id not in scan_results
