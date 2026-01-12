# Tests Documentation - RunCoach AI Platform

## Overview

This directory contains all tests for the RunCoach AI backend API. Tests are organized into unit tests, integration tests, and end-to-end (E2E) tests.

## Test Structure

```
backend/tests/
├── __init__.py
├── conftest.py              # Pytest fixtures and configuration
├── fixtures/                # Test fixtures and sample data
│   └── sample_workout.py
├── e2e/                     # End-to-end tests
│   ├── __init__.py
│   ├── test_complete_user_flow.py
│   ├── test_training_plans_e2e.py
│   └── test_workouts_e2e.py
├── test_auth.py            # Authentication endpoint tests
├── test_coach.py           # Coach endpoint tests
├── test_endpoints.py       # General endpoint tests
├── test_health.py          # Health endpoint tests
├── test_integration.py     # Integration tests
├── test_profile.py         # Profile endpoint tests
├── test_regression.py      # Regression tests for complete flows
├── test_services.py        # Service layer tests
├── test_training_plans.py  # Training plans endpoint tests
├── test_utils.py           # Utility function tests
└── test_workouts.py        # Workouts endpoint tests
```

## Running Tests

### Prerequisites

Install test dependencies:

```bash
cd backend
pip install -r requirements-test.txt
```

Or install pytest and dependencies manually:

```bash
pip install pytest pytest-asyncio fastapi[all] httpx sqlalchemy
```

### Run All Tests

```bash
cd backend
pytest tests/
```

### Run Specific Test File

```bash
pytest tests/test_auth.py
```

### Run Specific Test Class

```bash
pytest tests/test_auth.py::TestAuthLogin
```

### Run Specific Test Method

```bash
pytest tests/test_auth.py::TestAuthLogin::test_login_success
```

### Run with Verbose Output

```bash
pytest tests/ -v
```

### Run with Coverage

```bash
pytest tests/ --cov=app --cov-report=html
```

## Test Categories

### Unit Tests

Test individual components in isolation:
- `test_auth.py` - Authentication logic
- `test_coach.py` - Coach service endpoints
- `test_health.py` - Health metrics endpoints
- `test_profile.py` - Profile management endpoints
- `test_training_plans.py` - Training plan endpoints
- `test_workouts.py` - Workout endpoints
- `test_services.py` - Service layer logic

### Integration Tests

Test component interactions:
- `test_endpoints.py` - Endpoint integration tests
- `test_integration.py` - Full integration tests

### Regression Tests

Test complete user flows to prevent regressions:
- `test_regression.py` - Complete user workflows

### End-to-End (E2E) Tests

Test complete flows against real/staging environment:
- `e2e/test_complete_user_flow.py` - Complete user journey
- `e2e/test_training_plans_e2e.py` - Training plans workflow
- `e2e/test_workouts_e2e.py` - Workouts workflow

## Running E2E Tests

E2E tests are designed to run against a real API (production or staging).

### Prerequisites

1. Have a valid access token or credentials
2. Set the `API_URL` environment variable

### Run E2E Tests

#### Complete User Flow

```bash
cd backend/tests/e2e
export API_URL=https://your-api-url.com
python test_complete_user_flow.py
```

This test will:
1. Register a new user
2. Login
3. Update profile
4. Create workout
5. Generate training plan
6. View progress

#### Training Plans E2E

```bash
export API_URL=https://your-api-url.com
export ACCESS_TOKEN=your_access_token_here
python test_training_plans_e2e.py $ACCESS_TOKEN
```

#### Workouts E2E

```bash
export API_URL=https://your-api-url.com
export ACCESS_TOKEN=your_access_token_here
python test_workouts_e2e.py $ACCESS_TOKEN
```

## Test Fixtures

### Available Fixtures (in `conftest.py`)

- `test_db` - In-memory SQLite database session
- `test_client` - FastAPI TestClient
- `test_user_data` - Sample user data for registration
- `another_user_data` - Another sample user
- `registered_user` - Pre-registered user with tokens

### Using Fixtures

```python
def test_example(test_client: TestClient, registered_user: dict):
    token = registered_user["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = test_client.get("/api/v1/profile/", headers=headers)
    assert response.status_code == 200
```

## Writing New Tests

### Test File Structure

```python
"""
Tests for [Module Name] endpoints.

Tests all [module] endpoints with:
- Authentication verification
- Request/Response validation
- Error handling
- Edge cases
"""

import pytest
from fastapi.testclient import TestClient


class TestModuleEndpoint:
    """Test suite for [Endpoint]"""

    def test_endpoint_success(self, test_client: TestClient, registered_user: dict):
        """Test successful endpoint call"""
        token = registered_user["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = test_client.get("/api/v1/endpoint", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "expected_field" in data

    def test_endpoint_requires_authentication(self, test_client: TestClient):
        """Test that endpoint requires authentication"""
        response = test_client.get("/api/v1/endpoint")
        
        assert response.status_code == 401
```

### Test Naming Conventions

- Test files: `test_*.py`
- Test classes: `Test*` (e.g., `TestAuthLogin`)
- Test methods: `test_*` (e.g., `test_login_success`)

### Best Practices

1. **One assertion per test** when possible
2. **Use descriptive test names** that explain what is being tested
3. **Use fixtures** for common setup
4. **Mock external services** (AI, third-party APIs)
5. **Test edge cases** (missing fields, invalid data, etc.)
6. **Test authentication** requirements
7. **Test error handling** (404, 422, 500, etc.)

## Continuous Integration (CI/CD)

Tests should run automatically on:
- Pull requests
- Commits to main branch
- Scheduled runs

### GitHub Actions

If using GitHub Actions, create `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r backend/requirements-test.txt
      - run: pytest backend/tests/
```

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure you're running from the backend directory
2. **Database errors**: Tests use in-memory SQLite, should work automatically
3. **Authentication errors**: Use `registered_user` fixture for authenticated tests
4. **Mock errors**: Ensure mocks are patched correctly for external services

### Debugging Tests

Run with `-s` to see print statements:

```bash
pytest tests/test_auth.py -s
```

Run with `--pdb` to drop into debugger on failure:

```bash
pytest tests/test_auth.py --pdb
```

## Coverage Goals

Target coverage:
- **Unit tests**: 80%+ coverage
- **Integration tests**: Critical paths covered
- **E2E tests**: Main user flows covered

Check coverage:

```bash
pytest tests/ --cov=app --cov-report=term-missing
```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/core/testing.html)

## Contributing

When adding new features:

1. Write tests first (TDD) or alongside feature
2. Ensure all tests pass
3. Aim for good test coverage
4. Update this README if adding new test categories

---

**Last Updated:** 2026-01-10
