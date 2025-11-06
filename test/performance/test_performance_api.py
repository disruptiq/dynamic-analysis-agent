"""
Performance tests for API endpoints.
"""

import time
import json
import statistics
from unittest.mock import patch
import pytest

from src.api import app


@pytest.mark.performance
class TestAPIPerformance:
    """Performance tests for API endpoints."""

    def setup_method(self):
        """Setup before each test."""
        self.client = app.test_client()

    def test_health_endpoint_performance(self):
        """Test health endpoint response time."""
        response_times = []

        # Make multiple requests to measure performance
        num_requests = 100

        for _ in range(num_requests):
            start_time = time.time()
            response = self.client.get('/api/v1/health')
            end_time = time.time()

            assert response.status_code == 200
            response_times.append(end_time - start_time)

        # Calculate statistics
        avg_time = statistics.mean(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        p95_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile

        print(f"Health endpoint performance:")
        print(f"  Average response time: {avg_time:.4f}s")
        print(f"  Min response time: {min_time:.4f}s")
        print(f"  Max response time: {max_time:.4f}s")
        print(f"  95th percentile: {p95_time:.4f}s")

        # Performance assertions
        assert avg_time < 0.1  # Average should be under 100ms
        assert max_time < 0.5  # Max should be under 500ms
        assert p95_time < 0.2  # 95th percentile under 200ms

    def test_config_endpoint_performance(self):
        """Test config endpoint response time."""
        response_times = []

        num_requests = 50

        for _ in range(num_requests):
            start_time = time.time()
            response = self.client.get('/api/v1/config')
            end_time = time.time()

            assert response.status_code == 200
            response_times.append(end_time - start_time)

        avg_time = statistics.mean(response_times)
        max_time = max(response_times)

        print(f"Config endpoint performance:")
        print(f"  Average response time: {avg_time:.4f}s")
        print(f"  Max response time: {max_time:.4f}s")

        assert avg_time < 0.05  # Should be very fast
        assert max_time < 0.2

    @patch('src.api.threading.Thread')
    def test_scan_creation_performance(self, mock_thread):
        """Test scan creation performance."""
        response_times = []

        num_requests = 20

        for i in range(num_requests):
            start_time = time.time()
            response = self.client.post('/api/v1/scans',
                                      data=json.dumps({'image': f'perf-test-app-{i}'}),
                                      content_type='application/json')
            end_time = time.time()

            assert response.status_code == 201
            response_times.append(end_time - start_time)

        avg_time = statistics.mean(response_times)
        max_time = max(response_times)

        print(f"Scan creation performance:")
        print(f"  Average response time: {avg_time:.4f}s")
        print(f"  Max response time: {max_time:.4f}s")

        assert avg_time < 0.1  # Should be reasonably fast
        assert max_time < 0.5

    def test_list_scans_performance_empty(self):
        """Test list scans performance with empty list."""
        response_times = []

        num_requests = 50

        for _ in range(num_requests):
            start_time = time.time()
            response = self.client.get('/api/v1/scans')
            end_time = time.time()

            assert response.status_code == 200
            response_times.append(end_time - start_time)

        avg_time = statistics.mean(response_times)
        max_time = max(response_times)

        print(f"List scans (empty) performance:")
        print(f"  Average response time: {avg_time:.4f}s")
        print(f"  Max response time: {max_time:.4f}s")

        assert avg_time < 0.05
        assert max_time < 0.2

    @patch('src.api.threading.Thread')
    def test_list_scans_performance_with_data(self, mock_thread):
        """Test list scans performance with multiple scans."""
        # Create some scans first
        num_scans = 10
        scan_ids = []

        for i in range(num_scans):
            response = self.client.post('/api/v1/scans',
                                      data=json.dumps({'image': f'list-test-app-{i}'}),
                                      content_type='application/json')
            assert response.status_code == 201
            data = json.loads(response.data)
            scan_ids.append(data['scan_id'])

        # Now test listing performance
        response_times = []
        num_requests = 30

        for _ in range(num_requests):
            start_time = time.time()
            response = self.client.get('/api/v1/scans')
            end_time = time.time()

            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data['scans']) == num_scans
            response_times.append(end_time - start_time)

        avg_time = statistics.mean(response_times)
        max_time = max(response_times)

        print(f"List scans ({num_scans} scans) performance:")
        print(f"  Average response time: {avg_time:.4f}s")
        print(f"  Max response time: {max_time:.4f}s")

        assert avg_time < 0.1
        assert max_time < 0.3

    def test_get_scan_performance(self):
        """Test individual scan retrieval performance."""
        # Create a scan first
        response = self.client.post('/api/v1/scans',
                                  data=json.dumps({'image': 'get-test-app'}),
                                  content_type='application/json')
        assert response.status_code == 201
        data = json.loads(response.data)
        scan_id = data['scan_id']

        # Test retrieval performance
        response_times = []
        num_requests = 50

        for _ in range(num_requests):
            start_time = time.time()
            response = self.client.get(f'/api/v1/scans/{scan_id}')
            end_time = time.time()

            assert response.status_code == 200
            response_times.append(end_time - start_time)

        avg_time = statistics.mean(response_times)
        max_time = max(response_times)

        print(f"Get scan performance:")
        print(f"  Average response time: {avg_time:.4f}s")
        print(f"  Max response time: {max_time:.4f}s")

        assert avg_time < 0.05
        assert max_time < 0.2

    def test_memory_usage_stress_test(self):
        """Stress test to check for memory leaks in scan operations."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Perform many operations
        num_operations = 100

        with patch('src.api.threading.Thread'):
            for i in range(num_operations):
                # Create scan
                response = self.client.post('/api/v1/scans',
                                          data=json.dumps({'image': f'stress-test-{i}'}),
                                          content_type='application/json')
                assert response.status_code == 201

                # List scans
                response = self.client.get('/api/v1/scans')
                assert response.status_code == 200

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        print(f"Memory usage stress test:")
        print(f"  Initial memory: {initial_memory:.2f} MB")
        print(f"  Final memory: {final_memory:.2f} MB")
        print(f"  Memory increase: {memory_increase:.2f} MB")

        # Allow some memory increase but not excessive
        assert memory_increase < 50  # Less than 50MB increase for 100 operations

    def test_concurrent_request_simulation(self):
        """Simulate concurrent requests to test thread safety."""
        import threading

        results = []
        errors = []

        def make_request(request_id):
            try:
                start_time = time.time()
                response = self.client.get('/api/v1/health')
                end_time = time.time()

                results.append({
                    'id': request_id,
                    'status': response.status_code,
                    'time': end_time - start_time
                })
            except Exception as e:
                errors.append({'id': request_id, 'error': str(e)})

        # Create multiple threads
        threads = []
        num_threads = 10

        for i in range(num_threads):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)

        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        total_time = time.time() - start_time

        print(f"Concurrent request simulation ({num_threads} threads):")
        print(f"  Total time: {total_time:.4f}s")
        print(f"  Successful requests: {len(results)}")
        print(f"  Errors: {len(errors)}")

        # All requests should succeed
        assert len(results) == num_threads
        assert len(errors) == 0

        # Calculate response time statistics
        response_times = [r['time'] for r in results]
        avg_time = statistics.mean(response_times)
        max_time = max(response_times)

        print(f"  Average response time: {avg_time:.4f}s")
        print(f"  Max response time: {max_time:.4f}s")

        # Performance should still be reasonable under concurrency
        assert avg_time < 0.2
        assert max_time < 1.0
