# CramBrain Test Suite

This directory contains unit tests for both the backend (Python/FastAPI) and frontend (Next.js/React) components of CramBrain.

## Structure

```
tests/
├── backend/           # Backend unit tests (Python/pytest)
│   ├── test_utils_id.py
│   ├── test_models_types.py
│   └── test_api_endpoints.py
├── frontend/          # Frontend unit tests (TypeScript/Jest)
│   ├── components/
│   │   ├── Button.test.tsx
│   │   └── FileDrop.test.tsx
│   └── utils.test.ts
└── conftest.py        # Pytest configuration and fixtures
```

## Backend Tests

### Running Backend Tests

```bash
# Install dependencies (if not already installed)
cd apps/api
pip install -r requirements.txt

# Run all tests
pytest

# Run specific test file
pytest tests/backend/test_utils_id.py

# Run with coverage
pytest --cov=apps.api.src --cov-report=html

# Run with verbose output
pytest -v
```

### Backend Test Coverage

- **Utils**: ID generation, filename sanitization, file hashing
- **Models**: Pydantic model validation
- **API Endpoints**: Health checks, request/response validation
- **Services**: RAG services (embedding, search, quiz generation)

## Frontend Tests

### Setup

```bash
# Install dependencies (from project root)
npm install

# Run tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

### Frontend Test Coverage

- **Utils**: File size formatting, date formatting, PDF validation
- **Components**: Button, FileDrop, and other UI components
- **API Client**: API request/response handling
- **Hooks**: Custom React hooks

## Writing New Tests

### Backend Test Example

```python
# tests/backend/test_my_feature.py
import pytest
from apps.api.src.my_module import my_function

def test_my_function():
    result = my_function("input")
    assert result == "expected_output"
```

### Frontend Test Example

```typescript
// tests/frontend/components/MyComponent.test.tsx
import { render, screen } from '@testing-library/react'
import { MyComponent } from '@/components/MyComponent'

describe('MyComponent', () => {
  it('should render correctly', () => {
    render(<MyComponent />)
    expect(screen.getByText('Hello')).toBeInTheDocument()
  })
})
```

## Test Configuration

### Pytest Configuration

See `pytest.ini` for pytest configuration:
- Test discovery patterns
- Async test support
- Markers for test categorization

### Jest Configuration

See `jest.config.js` and `jest.setup.js` for Jest configuration:
- Next.js integration
- React Testing Library setup
- Module path aliases
- Environment mocks

## Continuous Integration

Tests should be run in CI/CD pipeline:
- Backend tests: Run on every push to main/develop
- Frontend tests: Run on every push to main/develop
- Coverage reports: Generate and track coverage metrics

## Best Practices

1. **Write tests first** (TDD) when possible
2. **Keep tests isolated** - each test should be independent
3. **Use meaningful test names** - describe what is being tested
4. **Mock external dependencies** - don't make real API calls in unit tests
5. **Test edge cases** - invalid inputs, error conditions
6. **Maintain test coverage** - aim for >80% coverage

## Troubleshooting

### Backend Tests

- **Import errors**: Ensure `apps/api/src` is in Python path
- **Missing dependencies**: Install all requirements from `requirements.txt`
- **Async tests**: Use `pytest-asyncio` for async function tests

### Frontend Tests

- **Module resolution errors**: Check `jest.config.js` path aliases
- **Next.js errors**: Ensure `next/jest` is properly configured
- **React hooks errors**: Use `@testing-library/react-hooks` if needed

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Jest Documentation](https://jestjs.io/)
- [React Testing Library](https://testing-library.com/react)
- [Next.js Testing](https://nextjs.org/docs/testing)

