# Testing Guide

## Quick Start

### Prerequisites
- Docker must be running (required for PostgreSQL testcontainers)
- Python 3.13+ with uv installed

### Run Tests

```bash
# Run all automated specification tests (recommended)
uv run pytest tests/integration/test_automated_spec.py -v

# Run all tests
uv run pytest tests/ -v

# Run with coverage report
uv run pytest tests/ --cov=backend/app --cov-report=term-missing

# Run specific test class
uv run pytest tests/integration/test_automated_spec.py::TestUsers -v

# Run specific test
uv run pytest tests/integration/test_automated_spec.py::TestHealth::test_health_endpoint -v
```

## Test Structure

### Automated Specification Tests
Location: `tests/integration/test_automated_spec.py`

These tests match the requirements in `AUTOMATED_TESTS.md` and verify:

1. **Health Endpoint** (1 test)
   - GET /health returns 200 with status="ok"

2. **User Endpoints** (8 tests)
   - POST /users/bulk - CSV import
   - GET /users - List all users
   - GET /users/<id> - Get user by ID
   - POST /users - Create user
   - PUT /users/<id> - Update user
   - Validation error handling

3. **URL Endpoints** (6 tests)
   - POST /urls - Create short URL
   - GET /urls - List URLs (with optional filtering)
   - GET /urls/<id> - Get URL by ID
   - PUT /urls/<id> - Update URL
   - Error handling for missing users

4. **Events/Analytics** (1 test)
   - GET /events - List all events

5. **Edge Cases** (4 tests)
   - 404 handling for missing resources
   - URL format validation
   - Required field validation

## Database Setup

### PostgreSQL with Testcontainers
Tests automatically spin up a PostgreSQL container for each test session:
- No manual database setup required
- Isolated test environment
- Automatic cleanup after tests complete

### Configuration
The test database is configured in `tests/conftest.py`:
- Uses PostgreSQL 16 Alpine image
- Connection pooling enabled
- Tables created automatically before tests
- Data cleaned between tests for isolation

## Test Fixtures

### Available Fixtures
- `app` - Flask application with PostgreSQL database
- `client` - Test client for making HTTP requests
- `test_user` - Pre-created test user for URL tests
- `postgres_container` - PostgreSQL testcontainer instance

### Database Isolation
Each test runs with a clean database:
- Tables are truncated before each test
- Foreign key constraints respected
- No data leakage between tests

## Writing New Tests

### Example Test
```python
def test_my_endpoint(client):
    """Test description"""
    # Create test data
    response = client.post("/users", json={
        "username": "testuser",
        "email": "test@example.com"
    })
    
    # Assertions
    assert response.status_code == 201
    data = response.get_json()
    assert data["username"] == "testuser"
```

### Best Practices
1. Use descriptive test names
2. Follow AAA pattern (Arrange, Act, Assert)
3. Test both success and error cases
4. Clean up test data (handled automatically)
5. Use fixtures for common setup

## Troubleshooting

### Docker Not Running
```
Error: Cannot connect to Docker daemon
```
**Solution**: Start Docker Desktop or Docker daemon

### Port Conflicts
```
Error: Port 5432 already in use
```
**Solution**: Testcontainers automatically assigns random ports, but if issues persist, stop other PostgreSQL instances

### Slow Tests
- First run downloads PostgreSQL image (one-time)
- Subsequent runs reuse the image
- Container startup takes ~2-3 seconds

### Test Failures
1. Check Docker is running
2. Verify all dependencies installed: `uv sync`
3. Check test output for specific error messages
4. Run with `-v` flag for verbose output

## CI/CD Integration

### GitHub Actions Example
```yaml
- name: Run tests
  run: |
    docker pull postgres:16-alpine
    uv run pytest tests/ -v
```

### Requirements
- Docker available in CI environment
- Sufficient permissions to run containers
- Network access to pull Docker images

## Coverage Goals
- Overall: 85%+ ✅
- Controllers: 80%+
- Services: 90%+
- Models: 95%+
- Repositories: 85%+

Current coverage: **85%**
