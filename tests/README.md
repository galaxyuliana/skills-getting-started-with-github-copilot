# FastAPI Test Suite Documentation

This directory contains comprehensive tests for the High School Management System FastAPI application.

## Test Structure

### 📁 Test Files

- **`test_api.py`** - API endpoint tests
- **`test_models.py`** - Data model and business logic tests  
- **`test_performance.py`** - Performance and load tests
- **`conftest.py`** - Shared fixtures and test configuration

### 🧪 Test Categories

#### API Endpoint Tests (`test_api.py`)
- **Root Endpoint Tests**: Verify redirect behavior
- **Activities Endpoint Tests**: Test activity listing functionality
- **Signup Endpoint Tests**: Test student registration for activities
- **Unregister Endpoint Tests**: Test student removal from activities
- **End-to-End Workflow Tests**: Complete signup/unregister workflows
- **Error Handling Tests**: Edge cases and error conditions

#### Data Model Tests (`test_models.py`)
- **Data Model Structure**: Validate activity data structure
- **Business Logic**: Test capacity constraints and rules
- **Data Integrity**: Ensure data consistency
- **Activity Manipulation**: Test direct data operations

#### Performance Tests (`test_performance.py`)
- **Response Time Tests**: Measure API response times
- **Concurrent Load Tests**: Test handling of simultaneous requests
- **Stress Tests**: Test behavior under high load
- **Resource Usage Tests**: Monitor memory usage and stability

## 🚀 Running Tests

### Prerequisites
```bash
# Install dependencies
pip install -r requirements.txt
```

### Quick Start
```bash
# Run all tests (excluding slow tests)
python -m pytest tests/ -v

# Or use the test runner script
./run_tests.sh
```

### Specific Test Commands

```bash
# Run only API tests
python -m pytest tests/test_api.py -v

# Run only data model tests  
python -m pytest tests/test_models.py -v

# Run performance tests (excluding slow ones)
python -m pytest tests/test_performance.py -v -m "not slow"

# Run slow tests
python -m pytest tests/ -v -m "slow"

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run specific test class
python -m pytest tests/test_api.py::TestSignupEndpoint -v

# Run specific test method
python -m pytest tests/test_api.py::TestSignupEndpoint::test_signup_success -v
```

### Test Markers
- **`@pytest.mark.slow`** - Marks tests that take longer to run (5+ seconds)

## 📊 Test Coverage

The test suite provides comprehensive coverage of:

### ✅ API Endpoints
- `GET /` (root redirect)
- `GET /activities` (list all activities)
- `POST /activities/{activity_name}/signup` (register student)
- `DELETE /activities/{activity_name}/unregister` (unregister student)

### ✅ Business Logic
- Activity capacity management
- Duplicate registration prevention
- Email format validation
- URL encoding handling
- Error response formatting

### ✅ Data Integrity
- Activity structure validation
- Participant list consistency
- Capacity constraint enforcement
- Data state management

### ✅ Performance Characteristics
- Response time validation (< 1 second)
- Concurrent request handling
- Memory usage stability
- Sustained load capability (10+ requests/second)

## 🔧 Test Configuration

### Fixtures
- **`client`** - FastAPI test client
- **`reset_activities`** - Resets activity data before/after each test
- **`sample_activity`** - Provides sample activity data

### pytest.ini Configuration
```ini
[pytest]
pythonpath = .
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

## 🐛 Debugging Tests

### Running with Debugging
```bash
# Run with detailed output
python -m pytest tests/ -v -s

# Run with pdb on failure
python -m pytest tests/ --pdb

# Run with extra test summary
python -m pytest tests/ -v --tb=long

# Run specific failing test with debug info
python -m pytest tests/test_api.py::TestSignupEndpoint::test_signup_success -v -s
```

### Common Issues

1. **Import Errors**: Ensure you're running from the project root
2. **Fixture Issues**: Check that `reset_activities` is used in tests that modify data
3. **Async Issues**: Use `pytest-asyncio` for async test functions
4. **Server Running**: Tests use TestClient, no need for running server

## 📈 Adding New Tests

### Test Naming Convention
- Test files: `test_*.py`
- Test classes: `Test*` 
- Test methods: `test_*`

### Example Test Structure
```python
class TestNewFeature:
    """Test cases for new feature."""
    
    def test_new_feature_success(self, client, reset_activities):
        """Test successful operation."""
        # Arrange
        test_data = {...}
        
        # Act
        response = client.post("/api/endpoint", json=test_data)
        
        # Assert
        assert response.status_code == 200
        assert response.json()["success"] == True
    
    def test_new_feature_error(self, client, reset_activities):
        """Test error handling."""
        # Test error conditions...
```

### Performance Test Guidelines
- Mark long-running tests with `@pytest.mark.slow`
- Keep performance assertions reasonable
- Test both success and failure scenarios
- Monitor resource usage for memory leaks

## 📝 Test Reports

### Generating HTML Coverage Report
```bash
pip install pytest-cov
python -m pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
```

### Generating JUnit XML Report
```bash
python -m pytest tests/ --junitxml=test-results.xml
```

## 🤝 Contributing

When adding new features:
1. Write tests first (TDD approach)
2. Ensure all existing tests pass
3. Add appropriate test markers
4. Update this documentation if needed
5. Run the full test suite before submitting

---

**Test Suite Statistics:**
- Total Tests: 38
- API Tests: 18
- Model Tests: 12
- Performance Tests: 8
- Average Runtime: ~1.5 seconds (excluding slow tests)