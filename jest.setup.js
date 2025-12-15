import '@testing-library/jest-dom'

jest.mock('next/navigation', () => ({
  useRouter() {
    return {
      push: jest.fn(),
      replace: jest.fn(),
      prefetch: jest.fn(),
      back: jest.fn(),
      pathname: '/',
      query: {},
      asPath: '/',
    }
  },
  usePathname() {
    return '/'
  },
  useSearchParams() {
    return new URLSearchParams()
  },
}))

process.env.NEXT_PUBLIC_API_BASE_URL = 'https://test-api.example.com'

global.console = {
  ...console,
  error: jest.fn(),
  warn: jest.fn(),
}

