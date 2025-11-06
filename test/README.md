# Testing Framework for Dynamic Analysis Agent

This directory contains a comprehensive testing framework for the Dynamic Analysis Agent, implementing unit tests, integration tests, end-to-end tests, performance tests, load tests, and security tests.

## Test Structure

### 📁 Directory Organization

```
test/
├── unit/                      # Unit tests (45 tests)
│   ├── test_config.py         # Configuration management tests
│   ├── test_logger.py         # Logging system tests
│   ├── test_utils.py          # Utility functions tests
│   ├── test_api.py            # API endpoint tests
│   └── test_nmap_scanner.py   # Nmap integration tests
├── integration/               # Integration tests (12 tests)
│   ├── test_integration_api_config.py  # API + config interaction
│   └── test_integration_api_logger.py  # API + logger interaction
├── e2e/                       # End-to-end tests (8 tests)
│   └── test_e2e_scan_workflow.py  # Complete scan workflows
├── performance/               # Performance tests (9 tests)
│   └── test_performance_api.py # API performance benchmarks
├── load/                      # Load tests (8 tests)
│   └── test_load_api.py       # High-load API testing
├── security/                  # Security tests (8 tests)
│   └── test_security_agent.py # Agent security testing
├── conftest.py                # Shared fixtures and configuration
├── pytest.ini                 # Pytest settings and coverage configuration
├── README.md                  # Testing framework documentation
├── vulnerable_app.py          # Test target application
├── docker-compose.yml         # Test environment orchestration
├── Dockerfile                 # Test app containerization
├── requirements.txt           # Test dependencies
└── test_basic.py              # Basic functionality tests
```

### 🧪 Test Categories

#### Unit Tests (`pytest -m unit`)
Located in `test/unit/` - Test individual components in isolation:
- **test_config.py**: Configuration management testing
- **test_logger.py**: Logging utilities testing
- **test_utils.py**: Utility functions testing
- **test_api.py**: API endpoint testing
- **test_nmap_scanner.py**: Nmap scanner tool testing

#### Integration Tests (`pytest -m integration`)
Located in `test/integration/` - Test component interactions:
- **test_integration_api_config.py**: API and configuration interaction
- **test_integration_api_logger.py**: API and logging interaction

#### End-to-End Tests (`pytest -m e2e`)
Located in `test/e2e/` - Test complete user workflows:
- **test_e2e_scan_workflow.py**: Complete scan workflow testing

#### Performance Tests (`pytest -m performance`)
Located in `test/performance/` - Benchmark system performance:
- **test_performance_api.py**: API endpoint performance benchmarking

#### Load Tests (`pytest -m load`)
Located in `test/load/` - Test system under high load:
- **test_load_api.py**: High-load API testing

#### Security Tests (`pytest -m security`)
Located in `test/security/` - Test agent security:
- **test_security_agent.py**: Security testing of the agent codebase

## Configuration

### pytest.ini
Contains pytest configuration including:
- Test discovery patterns
- Coverage settings (80% minimum coverage required)
- Custom markers
- Test output formatting

### conftest.py
Shared fixtures and configuration:
- `api_client`: Flask test client
- `clean_scan_state`: Clean scan state for tests
- `mock_config`, `mock_logger`, `mock_subprocess`: Common mocks
- Sample test data fixtures

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test Categories
```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# End-to-end tests only
pytest -m e2e

# Performance tests only
pytest -m performance

# Load tests only
pytest -m load

# Security tests only
pytest -m security
```

### Run Specific Test Files
```bash
pytest test/unit/test_config.py
pytest test/unit/test_api.py -v
pytest test/integration/test_integration_api_config.py
pytest test/performance/test_performance_api.py
```

### Run with Coverage
```bash
pytest --cov=src --cov-report=html
```

### Run Performance Tests (with detailed output)
```bash
pytest -m performance -v -s
```

## Test Categories Explained

### Unit Tests
Test individual components in isolation using mocks and stubs. Focus on:
- Function correctness
- Error handling
- Edge cases
- Input validation

### Integration Tests
Test interaction between multiple components:
- API with configuration
- API with logging
- Component interoperability

### End-to-End Tests
Test complete user workflows:
- Scan creation to completion
- Error scenarios
- Cancellation workflows

### Performance Tests
Benchmark system performance:
- Response times
- Memory usage
- Throughput metrics

### Load Tests
Test system under high load:
- Concurrent operations
- Sustained load
- Memory usage under load

### Security Tests
Test agent security:
- Input validation
- Injection prevention
- Information disclosure
- File access restrictions

## Coverage Requirements

- Minimum 80% code coverage required
- Coverage reports generated in HTML format
- Coverage failures will cause test suite to fail

## Continuous Integration

The test suite is designed to run in CI/CD pipelines:

1. Unit and integration tests run on every commit
2. Performance tests run on release branches
3. Load and security tests run nightly
4. Coverage reports uploaded to CI dashboard

## Adding New Tests

### For Unit Tests
```python
import pytest
from src.module import function_to_test

class TestModuleName:
    def test_function_name(self):
        # Arrange
        # Act
        # Assert
        pass
```

### For Integration Tests
```python
@pytest.mark.integration
class TestComponentInteraction:
    def test_api_config_integration(self, api_client, mock_config):
        # Test interaction between API and config
        pass
```

### For Performance Tests
```python
@pytest.mark.performance
class TestPerformance:
    def test_endpoint_performance(self, api_client):
        # Measure response times
        # Assert performance requirements
        pass
```

## Mocking Strategy

- External dependencies (Docker, network tools) are mocked
- File system operations use temporary files
- API responses are mocked for external services
- Time-dependent operations use fixed timestamps

## Test Data

Sample test data is provided through fixtures:
- `sample_scan_data`: Valid scan creation payload
- `sample_vulnerability`: Vulnerability data structure
- `sample_tool_result`: Tool execution result

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Descriptive Names**: Test names should describe what they test
3. **Minimal Assertions**: Assert only what's necessary
4. **Fast Execution**: Tests should run quickly
5. **Realistic Data**: Use realistic test data
6. **Error Scenarios**: Test both success and failure cases
7. **Documentation**: Document complex test scenarios

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure PYTHONPATH includes src directory
2. **Mock Issues**: Check that mocks are properly scoped
3. **Fixture Errors**: Ensure fixtures are properly defined
4. **Coverage Issues**: Check that source files are importable

### Debug Mode
```bash
pytest -v -s --pdb test_file.py::TestClass::test_method
```

### Profiling Tests
```bash
pytest --durations=10  # Show slowest 10 tests
```
