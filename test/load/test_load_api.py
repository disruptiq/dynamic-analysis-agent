"""
Load tests for API endpoints under high load.
"""

import time
import json
import threading
import statistics
from unittest.mock import patch
import pytest

from src.api import app, active_scans, scan_results


@pytest.mark.load
class TestAPILoad:
    """Load tests for API endpoints."""

    def setup_method(self):
        """Setup before each test."""
        active_scans.clear()
        scan_results.clear()
        self.client = app.test_client()

    def teardown_method(self):
        """Cleanup after each test."""
        active_scans.clear()
        scan_results.clear()

    def test_high_frequency_health_checks(self):
        """Test sustained high-frequency health checks."""
        num_requests = 1000
        response_times = []
        errors = []

        print(f"Starting high-frequency health check test ({num_requests} requests)...")

        for i in range(num_requests):
            try:
                start_time = time.time()
                response = self.client.get('/api/v1/health')
                end_time = time.time()

                if response.status_code == 200:
                    response_times.append(end_time - start_time)
                else:
                    errors.append(f"Request {i}: Status {response.status_code}")

                # Small delay to prevent overwhelming (but still test high frequency)
                if i % 100 == 0:
                    time.sleep(0.01)

            except Exception as e:
                errors.append(f"Request {i}: {str(e)}")

        # Analyze results
        success_rate = len(response_times) / num_requests * 100

        print(f"High-frequency health check results:")
        print(f"  Total requests: {num_requests}")
        print(f"  Successful responses: {len(response_times)}")
        print(f"  Errors: {len(errors)}")
        print(f"  Success rate: {success_rate:.2f}%")

        if response_times:
            avg_time = statistics.mean(response_times)
            max_time = max(response_times)
            p95_time = statistics.quantiles(response_times, n=20)[18]

            print(f"  Average response time: {avg_time:.4f}s")
            print(f"  Max response time: {max_time:.4f}s")
            print(f"  95th percentile: {p95_time:.4f}s")

            # Under load, performance may degrade but should remain reasonable
            assert success_rate > 99.0  # At least 99% success rate
            assert avg_time < 0.5  # Average under 500ms
            assert max_time < 2.0  # Max under 2 seconds

    def test_concurrent_scan_operations(self):
        """Test concurrent scan creation and monitoring."""
        num_concurrent_scans = 20
        results = {}
        errors = []

        def create_and_monitor_scan(scan_id):
            try:
                # Create scan
                response = self.client.post('/api/v1/scans',
                                          data=json.dumps({'image': f'load-test-app-{scan_id}'}),
                                          content_type='application/json')

                if response.status_code != 201:
                    errors.append(f"Failed to create scan {scan_id}: {response.status_code}")
                    return

                data = json.loads(response.data)
                actual_scan_id = data['scan_id']

                # Monitor scan status
                max_attempts = 10
                for attempt in range(max_attempts):
                    status_response = self.client.get(f'/api/v1/scans/{actual_scan_id}')
                    if status_response.status_code == 200:
                        status_data = json.loads(status_response.data)
                        if status_data.get('status') in ['completed', 'failed']:
                            results[scan_id] = {
                                'scan_id': actual_scan_id,
                                'status': status_data['status'],
                                'attempts': attempt + 1
                            }
                            break
                    time.sleep(0.1)  # Wait before retry
                else:
                    errors.append(f"Scan {scan_id} didn't complete within timeout")

            except Exception as e:
                errors.append(f"Exception in scan {scan_id}: {str(e)}")

        # Create threads for concurrent operations
        threads = []
        for i in range(num_concurrent_scans):
            thread = threading.Thread(target=create_and_monitor_scan, args=(i,))
            threads.append(thread)

        print(f"Starting concurrent scan test ({num_concurrent_scans} concurrent scans)...")
        start_time = time.time()

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        total_time = time.time() - start_time

        print(f"Concurrent scan results:")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Successful scans: {len(results)}")
        print(f"  Errors: {len(errors)}")
        print(f"  Success rate: {len(results)/num_concurrent_scans*100:.1f}%")

        # Analyze performance
        if results:
            avg_attempts = statistics.mean([r['attempts'] for r in results.values()])
            print(f"  Average status check attempts: {avg_attempts:.1f}")

        assert len(results) >= num_concurrent_scans * 0.9  # At least 90% success rate
        assert total_time < 30  # Should complete within 30 seconds

    @patch('src.api.threading.Thread')
    def test_memory_load_with_many_scans(self, mock_thread):
        """Test memory usage under load with many scan objects."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Create many scans
        num_scans = 500
        scan_ids = []

        print(f"Creating {num_scans} scans for memory load test...")

        for i in range(num_scans):
            response = self.client.post('/api/v1/scans',
                                      data=json.dumps({'image': f'memory-test-app-{i}'}),
                                      content_type='application/json')
            assert response.status_code == 201
            data = json.loads(response.data)
            scan_ids.append(data['scan_id'])

        intermediate_memory = process.memory_info().rss / 1024 / 1024  # MB

        # List all scans multiple times
        for _ in range(10):
            response = self.client.get('/api/v1/scans')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data['scans']) == num_scans

        list_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Get individual scans
        for scan_id in scan_ids[:50]:  # Test first 50
            response = self.client.get(f'/api/v1/scans/{scan_id}')
            assert response.status_code == 200

        final_memory = process.memory_info().rss / 1024 / 1024  # MB

        memory_increase = final_memory - initial_memory

        print(f"Memory load test results:")
        print(f"  Initial memory: {initial_memory:.2f} MB")
        print(f"  After {num_scans} scans: {intermediate_memory:.2f} MB")
        print(f"  After list operations: {list_memory:.2f} MB")
        print(f"  Final memory: {final_memory:.2f} MB")
        print(f"  Total increase: {memory_increase:.2f} MB")
        print(f"  Memory per scan: {memory_increase/num_scans*1024:.2f} KB")

        # Memory usage should scale reasonably
        assert memory_increase < 200  # Less than 200MB for 500 scans
        assert memory_increase / num_scans < 0.5  # Less than 0.5MB per scan

    def test_sustained_load_list_operations(self):
        """Test sustained load on list operations."""
        # Create initial scans
        initial_scans = 50
        for i in range(initial_scans):
            response = self.client.post('/api/v1/scans',
                                      data=json.dumps({'image': f'sustained-test-{i}'}),
                                      content_type='application/json')
            assert response.status_code == 201

        # Perform sustained list operations
        num_iterations = 100
        response_times = []

        print(f"Starting sustained load test ({num_iterations} list operations)...")

        start_time = time.time()
        for i in range(num_iterations):
            iter_start = time.time()
            response = self.client.get('/api/v1/scans')
            iter_end = time.time()

            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data['scans']) == initial_scans

            response_times.append(iter_end - iter_start)

            # Small delay between iterations
            time.sleep(0.01)

        total_time = time.time() - start_time

        avg_time = statistics.mean(response_times)
        max_time = max(response_times)
        min_time = min(response_times)

        print(f"Sustained load list operations results:")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Average response time: {avg_time:.4f}s")
        print(f"  Min response time: {min_time:.4f}s")
        print(f"  Max response time: {max_time:.4f}s")
        print(f"  Operations per second: {num_iterations/total_time:.1f}")

        # Performance should remain stable
        assert avg_time < 0.1  # Average under 100ms
        assert max_time < 0.5  # Max under 500ms
        assert num_iterations/total_time > 50  # At least 50 operations per second

    def test_mixed_load_operations(self):
        """Test mixed load with different operation types."""
        operation_counts = {
            'create': 0,
            'list': 0,
            'get': 0,
            'health': 0
        }
        response_times = []
        errors = []

        # Create some initial scans
        initial_scan_ids = []
        for i in range(10):
            response = self.client.post('/api/v1/scans',
                                      data=json.dumps({'image': f'mixed-test-{i}'}),
                                      content_type='application/json')
            assert response.status_code == 201
            data = json.loads(response.data)
            initial_scan_ids.append(data['scan_id'])

        # Perform mixed operations
        num_operations = 200

        print(f"Starting mixed load test ({num_operations} operations)...")

        for i in range(num_operations):
            try:
                start_time = time.time()

                # Randomly choose operation type
                import random
                operation = random.choice(['create', 'list', 'get', 'health'])

                if operation == 'create':
                    response = self.client.post('/api/v1/scans',
                                              data=json.dumps({'image': f'mixed-op-{i}'}),
                                              content_type='application/json')
                    operation_counts['create'] += 1
                elif operation == 'list':
                    response = self.client.get('/api/v1/scans')
                    operation_counts['list'] += 1
                elif operation == 'get':
                    scan_id = random.choice(initial_scan_ids)
                    response = self.client.get(f'/api/v1/scans/{scan_id}')
                    operation_counts['get'] += 1
                elif operation == 'health':
                    response = self.client.get('/api/v1/health')
                    operation_counts['health'] += 1

                end_time = time.time()

                if response.status_code in [200, 201]:
                    response_times.append(end_time - start_time)
                else:
                    errors.append(f"Operation {i} ({operation}): Status {response.status_code}")

            except Exception as e:
                errors.append(f"Operation {i}: {str(e)}")

        success_rate = len(response_times) / num_operations * 100

        print(f"Mixed load test results:")
        print(f"  Total operations: {num_operations}")
        print(f"  Successful operations: {len(response_times)}")
        print(f"  Errors: {len(errors)}")
        print(f"  Success rate: {success_rate:.1f}%")
        print(f"  Operation counts: {operation_counts}")

        if response_times:
            avg_time = statistics.mean(response_times)
            max_time = max(response_times)
            print(f"  Average response time: {avg_time:.4f}s")
            print(f"  Max response time: {max_time:.4f}s")

        assert success_rate > 95.0  # At least 95% success rate
        assert len(response_times) > 0  # Some operations should succeed
