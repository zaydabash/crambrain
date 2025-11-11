# Test Setup Guide

## Quick Start

### Backend Tests

1. **Install dependencies:**
   ```bash
   cd apps/api
   pip install -r requirements.txt
   ```

2. **Run tests:**
   ```bash
   # From project root
   pytest

   # Or from apps/api
   cd apps/api
   pytest ../../tests/backend
   ```

3. **Run with coverage:**
   ```bash
   pytest --cov=apps.api.src --cov-report=html
   ```

### Frontend Tests

1. **Install dependencies:**
   ```bash
   cd crambrain-web-standalone
   npm install
   ```

2. **Run tests:**
   ```bash
   npm test
   ```

3. **Run with coverage:**
   ```bash
   npm run test:coverage
   ```

## Test Files Created

### Backend
- ✅ `tests/backend/test_utils_id.py` - ID generation utilities
- ✅ `tests/backend/test_models_types.py` - Pydantic models
- ✅ `tests/backend/test_api_endpoints.py` - API endpoints
- ✅ `tests/conftest.py` - Pytest fixtures
- ✅ `pytest.ini` - Pytest configuration

### Frontend
- ✅ `crambrain-web-standalone/__tests__/lib/utils.test.ts` - Utility functions
- ✅ `crambrain-web-standalone/__tests__/components/Button.test.tsx` - Button component
- ✅ `crambrain-web-standalone/jest.config.js` - Jest configuration
- ✅ `crambrain-web-standalone/jest.setup.js` - Jest setup

## Next Steps

1. **Install frontend test dependencies:**
   ```bash
   cd crambrain-web-standalone
   npm install
   ```

2. **Run backend tests to verify setup:**
   ```bash
   pytest tests/backend/test_utils_id.py -v
   ```

3. **Run frontend tests to verify setup:**
   ```bash
   cd crambrain-web-standalone
   npm test
   ```

## Adding New Tests

### Backend Test Example
```python
# tests/backend/test_my_feature.py
import pytest

def test_my_function():
    result = my_function("input")
    assert result == "expected"
```

### Frontend Test Example
```typescript
// crambrain-web-standalone/__tests__/components/MyComponent.test.tsx
import { render, screen } from '@testing-library/react'
import { MyComponent } from '@/components/MyComponent'

describe('MyComponent', () => {
  it('should render', () => {
    render(<MyComponent />)
    expect(screen.getByText('Hello')).toBeInTheDocument()
  })
})
```

## Troubleshooting

### Backend
- **Import errors**: Make sure you're running from project root or add `apps/api/src` to PYTHONPATH
- **Missing dependencies**: Run `pip install -r requirements.txt`

### Frontend
- **Module resolution**: Check `jest.config.js` path aliases match `tsconfig.json`
- **Next.js errors**: Ensure `next/jest` is properly configured in `jest.config.js`

