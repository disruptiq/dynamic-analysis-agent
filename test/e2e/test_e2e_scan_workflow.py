"""
End-to-end tests for complete scan workflows.
"""

import json
import time
import pytest
from unittest.mock import patch, MagicMock

from src.api import app, active_scans, scan_results


@pytest.mark.e2e
class TestE2EScanWorkflow:
    """End-to-end tests for scan workflows."""

    def setup_method(self):
        """Setup before each test."""
        active_scans.clear()
        scan_results.clear()
        self.client = app.test_client()

    def teardown_method(self):
        """Cleanup after each test."""
        active_scans.clear()
        scan_results.clear()

    @patch('src.api.threading.Thread')
    @patch('src.api.perform_scan_async')
    def test_complete_scan_workflow_success(self, mock_perform_scan, mock_thread):
        """Test complete successful scan workflow from creation to completion."""
        # Mock the async scan to immediately complete
        def mock_scan_async(scan_id, image, port, url):
            active_scans[scan_id]['status'] = 'completed'
            scan_results[scan_id] = {
                'id': scan_id,
                'target': f'http://localhost:{port}',
                'status': 'completed',
                'timestamp': time.time(),
                'vulnerabilities': [
                    {'type': 'xss', 'severity': 'high', 'description': 'Test vulnerability'}
                ],
                'tools': [
                    {'name': 'nmap', 'results': {'open_ports': [80]}},
                    {'name': 'nikto', 'results': {'findings': []}}
                ],
                'summary': {
                    'total_vulnerabilities': 1,
                    'vulnerability_types': {'xss': 1},
                    'tools_run': 2,
                    'scan_duration': 10.5
                }
            }

        mock_perform_scan.side_effect = mock_scan_async

        # Step 1: Create scan
        create_response = self.client.post('/api/v1/scans',
                                         data=json.dumps({
                                             'image': 'vulnerable-web-app',
                                             'port': 8080
                                         }),
                                         content_type='application/json')

        assert create_response.status_code == 201
        create_data = json.loads(create_response.data)
        scan_id = create_data['scan_id']

        # Step 2: Check scan status (should be running/completed)
        status_response = self.client.get(f'/api/v1/scans/{scan_id}')
        assert status_response.status_code == 200
        status_data = json.loads(status_response.data)

        assert status_data['status'] == 'completed'
        assert status_data['target'] == 'http://localhost:8080'
        assert len(status_data['vulnerabilities']) == 1
        assert len(status_data['tools']) == 2
        assert status_data['summary']['total_vulnerabilities'] == 1

        # Step 3: List scans
        list_response = self.client.get('/api/v1/scans')
        assert list_response.status_code == 200
        list_data = json.loads(list_response.data)

        assert len(list_data['scans']) == 1
        assert list_data['scans'][0]['id'] == scan_id
        assert list_data['scans'][0]['status'] == 'completed'

        # Step 4: Delete scan
        delete_response = self.client.delete(f'/api/v1/scans/{scan_id}')
        assert delete_response.status_code == 200

        # Verify scan was deleted
        get_response = self.client.get(f'/api/v1/scans/{scan_id}')
        assert get_response.status_code == 404

    def test_scan_creation_validation_workflow(self):
        """Test the validation workflow for scan creation."""
        # Test missing image
        response = self.client.post('/api/v1/scans',
                                  data=json.dumps({'port': 8080}),
                                  content_type='application/json')
        assert response.status_code == 400

        # Test invalid JSON
        response = self.client.post('/api/v1/scans',
                                  data='not json',
                                  content_type='application/json')
        assert response.status_code == 400

        # Test successful creation
        with patch('src.api.threading.Thread'):
            response = self.client.post('/api/v1/scans',
                                      data=json.dumps({'image': 'test-app'}),
                                      content_type='application/json')
            assert response.status_code == 201

    @patch('src.api.threading.Thread')
    @patch('src.api.perform_scan_async')
    def test_multiple_scans_workflow(self, mock_perform_scan, mock_thread):
        """Test workflow with multiple concurrent scans."""
        def mock_scan_async(scan_id, image, port, url):
            time.sleep(0.1)  # Simulate processing time
            active_scans[scan_id]['status'] = 'completed'
            scan_results[scan_id] = {
                'id': scan_id,
                'target': f'http://localhost:{port}',
                'status': 'completed',
                'timestamp': time.time(),
                'vulnerabilities': [],
                'tools': [],
                'summary': {'total_vulnerabilities': 0, 'tools_run': 0}
            }

        mock_perform_scan.side_effect = mock_scan_async

        # Create multiple scans
        scan_ids = []
        for i in range(3):
            response = self.client.post('/api/v1/scans',
                                      data=json.dumps({
                                          'image': f'app-{i}',
                                          'port': 8080 + i
                                      }),
                                      content_type='application/json')
            assert response.status_code == 201
            data = json.loads(response.data)
            scan_ids.append(data['scan_id'])

        # List all scans
        response = self.client.get('/api/v1/scans')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['scans']) == 3

        # Check each scan individually
        for scan_id in scan_ids:
            response = self.client.get(f'/api/v1/scans/{scan_id}')
            assert response.status_code == 200
            scan_data = json.loads(response.data)
            assert scan_data['status'] == 'completed'

    @patch('src.api.threading.Thread')
    @patch('src.api.perform_scan_async')
    def test_scan_failure_workflow(self, mock_perform_scan, mock_thread):
        """Test workflow when scan fails."""
        def mock_scan_async(scan_id, image, port, url):
            active_scans[scan_id]['status'] = 'failed'
            active_scans[scan_id]['error'] = 'Container failed to start'

        mock_perform_scan.side_effect = mock_scan_async

        # Create scan
        response = self.client.post('/api/v1/scans',
                                  data=json.dumps({'image': 'failing-app'}),
                                  content_type='application/json')
        assert response.status_code == 201
        data = json.loads(response.data)
        scan_id = data['scan_id']

        # Check failed scan
        response = self.client.get(f'/api/v1/scans/{scan_id}')
        assert response.status_code == 200
        scan_data = json.loads(response.data)
        assert scan_data['status'] == 'failed'
        assert 'Container failed to start' in scan_data['error']

        # Failed scans should still appear in list
        response = self.client.get('/api/v1/scans')
        assert response.status_code == 200
        list_data = json.loads(response.data)
        assert len(list_data['scans']) == 1
        assert list_data['scans'][0]['status'] == 'failed'

    def test_health_and_config_endpoints_workflow(self):
        """Test health and config endpoints in workflow."""
        # Health check
        response = self.client.get('/api/v1/health')
        assert response.status_code == 200
        health_data = json.loads(response.data)
        assert health_data['status'] == 'healthy'
        assert 'timestamp' in health_data
        assert health_data['version'] == '1.0.0'

        # Config endpoint
        response = self.client.get('/api/v1/config')
        assert response.status_code == 200
        config_data = json.loads(response.data)
        assert 'docker' in config_data
        assert 'reporting' in config_data
        assert 'scanning' in config_data

    @patch('src.api.threading.Thread')
    def test_scan_cancellation_workflow(self, mock_thread):
        """Test scan cancellation workflow."""
        # Create scan
        response = self.client.post('/api/v1/scans',
                                  data=json.dumps({'image': 'test-app'}),
                                  content_type='application/json')
        assert response.status_code == 201
        data = json.loads(response.data)
        scan_id = data['scan_id']

        # Cancel scan
        response = self.client.delete(f'/api/v1/scans/{scan_id}')
        assert response.status_code == 200
        delete_data = json.loads(response.data)
        assert 'Scan cancelled' in delete_data['message']

        # Check scan status
        response = self.client.get(f'/api/v1/scans/{scan_id}')
        assert response.status_code == 200
        scan_data = json.loads(response.data)
        assert scan_data['status'] == 'cancelled'
