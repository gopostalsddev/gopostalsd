# Testing Guide for Go Postal SD Backend

This guide provides comprehensive information about the test suite designed to achieve 100% code coverage.

## Test Architecture

### Test Structure
```
tests/
├── unit/                    # Unit tests for individual components
│   ├── controllers/         # Controller layer tests
│   ├── services/           # Service layer tests
│   ├── repositories/       # Repository layer tests
│   ├── factories/          # Factory pattern tests
│   └── models/             # Model tests
├── integration/            # Integration tests
│   ├── api/               # API endpoint tests
│   ├── database/          # Database integration tests
│   └── external/          # External service integration tests
├── fixtures/              # Test fixtures and mocks
├── utils/                 # Test utilities and helpers
└── conftest.py           # Pytest configuration
```

## Test Categories

### 1. Unit Tests
- **Purpose**: Test individual components in isolation
- **Coverage**: 100% of all methods, functions, and classes
- **Mocking**: Extensive use of mocks to isolate components
- **Speed**: Fast execution (< 1 second per test)

### 2. Integration Tests
- **Purpose**: Test component interactions and data flow
- **Coverage**: All integration points between layers
- **Database**: Real database operations with test data
- **API**: Full HTTP request/response cycle testing

### 3. Performance Tests
- **Purpose**: Test system performance under load
- **Metrics**: Response time, memory usage, concurrent requests
- **Load**: Simulate realistic user loads
- **Stress**: Test system limits and error handling

## Running Tests

### Prerequisites
```bash
# Install test dependencies
pip install pytest pytest-cov pytest-xdist pytest-mock

# Install additional performance testing tools
pip install psutil
```

### Basic Test Execution
```bash
# Run all tests with coverage
python run_tests.py all

# Run specific test categories
python run_tests.py unit
python run_tests.py integration
python run_tests.py api
python run_tests.py performance

# Run fast tests only (exclude slow tests)
python run_tests.py fast

# Run tests in parallel
python run_tests.py parallel
```

### Advanced Test Execution
```bash
# Run specific test file
python run_tests.py specific --test-path tests/unit/services/test_pricing_service.py

# Run specific test function
python run_tests.py specific --test-path tests/unit/services/test_pricing_service.py::TestPricingService::test_get_product_options_success

# Generate coverage report only
python run_tests.py coverage
```

### Direct Pytest Commands
```bash
# Run all tests with verbose output
pytest tests/ -v

# Run with coverage and HTML report
pytest tests/ --cov=server --cov-report=html

# Run specific test category
pytest tests/unit/ -v
pytest tests/integration/ -v

# Run tests matching a pattern
pytest tests/ -k "test_pricing" -v

# Run tests with specific markers
pytest tests/ -m "unit" -v
pytest tests/ -m "performance" -v
```

## Test Coverage Goals

### Coverage Targets
- **Line Coverage**: 100%
- **Branch Coverage**: 100%
- **Function Coverage**: 100%
- **Class Coverage**: 100%

### Coverage Reports
- **Terminal**: Real-time coverage during test execution
- **HTML**: Detailed coverage report in `htmlcov/index.html`
- **XML**: Machine-readable coverage report for CI/CD

## Test Data Management

### Fixtures
- **Sample Data**: Realistic test data for all entities
- **Mock Objects**: Pre-configured mocks for external dependencies
- **Database**: Isolated test database with proper cleanup
- **Error Scenarios**: Comprehensive error condition testing

### Test Isolation
- **Database**: Each test gets a clean database state
- **Mocks**: Isolated mocking prevents test interference
- **Cleanup**: Automatic cleanup after each test
- **Parallel**: Tests can run in parallel without conflicts

## Performance Testing

### Load Testing
- **Concurrent Requests**: Test multiple simultaneous requests
- **Response Time**: Measure API response times
- **Memory Usage**: Monitor memory consumption
- **Database Performance**: Test database query performance

### Stress Testing
- **High Load**: Test system under maximum expected load
- **Error Handling**: Test error handling under stress
- **Recovery**: Test system recovery after stress
- **Resource Limits**: Test system resource limits

## Error Testing

### Error Scenarios
- **Database Errors**: Connection failures, query errors
- **API Errors**: External service failures, timeouts
- **Validation Errors**: Invalid input data
- **Network Errors**: Connection timeouts, network failures

### Error Recovery
- **Retry Logic**: Test retry mechanisms
- **Fallback**: Test fallback strategies
- **Graceful Degradation**: Test system behavior under errors
- **Logging**: Test error logging and monitoring

## Best Practices

### Test Writing
1. **Arrange-Act-Assert**: Clear test structure
2. **Descriptive Names**: Test names should describe the scenario
3. **Single Responsibility**: Each test should test one thing
4. **Independent**: Tests should not depend on each other
5. **Fast**: Tests should run quickly

### Mocking
1. **Isolate Dependencies**: Mock external dependencies
2. **Verify Interactions**: Assert mock method calls
3. **Realistic Data**: Use realistic mock data
4. **Error Scenarios**: Mock error conditions
5. **Cleanup**: Clean up mocks after tests

### Coverage
1. **100% Coverage**: Aim for complete coverage
2. **Meaningful Tests**: Don't just test for coverage
3. **Edge Cases**: Test boundary conditions
4. **Error Paths**: Test error handling paths
5. **Integration Points**: Test component interactions

## Continuous Integration

### CI/CD Integration
- **Automated Testing**: Run tests on every commit
- **Coverage Gates**: Fail builds if coverage drops below 100%
- **Performance Monitoring**: Track performance metrics
- **Quality Gates**: Enforce code quality standards

### Test Reports
- **Coverage Reports**: HTML and XML coverage reports
- **Performance Reports**: Performance test results
- **Test Results**: Detailed test execution results
- **Trends**: Track test performance over time

## Troubleshooting

### Common Issues
1. **Import Errors**: Check Python path and imports
2. **Database Issues**: Verify test database setup
3. **Mock Issues**: Check mock configurations
4. **Coverage Issues**: Verify test coverage completeness
5. **Performance Issues**: Check system resources

### Debug Tips
1. **Verbose Output**: Use `-v` flag for detailed output
2. **Single Test**: Run individual tests for debugging
3. **Print Statements**: Add debug prints to tests
4. **Mock Verification**: Check mock call arguments
5. **Database State**: Inspect database state during tests

## Maintenance

### Regular Tasks
1. **Update Tests**: Keep tests in sync with code changes
2. **Review Coverage**: Regularly review coverage reports
3. **Performance Monitoring**: Monitor test performance
4. **Dependency Updates**: Keep test dependencies updated
5. **Documentation**: Keep test documentation current

### Test Refactoring
1. **DRY Principle**: Don't repeat test code
2. **Helper Functions**: Create reusable test helpers
3. **Fixture Optimization**: Optimize test fixtures
4. **Test Data**: Centralize test data management
5. **Mock Reuse**: Reuse common mocks

This comprehensive test suite ensures the Go Postal SD backend maintains high quality, reliability, and performance while achieving 100% code coverage.
