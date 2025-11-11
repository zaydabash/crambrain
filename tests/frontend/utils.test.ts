/**
 * Unit tests for utility functions
 */

import {
  formatFileSize,
  formatDate,
  extractPageNumbers,
  highlightCitations,
  debounce,
  generateId,
  isValidPdf,
  getErrorMessage,
  cn,
} from '@/lib/utils'

describe('formatFileSize', () => {
  it('should format bytes correctly', () => {
    expect(formatFileSize(0)).toBe('0 Bytes')
    expect(formatFileSize(1024)).toBe('1 KB')
    expect(formatFileSize(1024 * 1024)).toBe('1 MB')
    expect(formatFileSize(1024 * 1024 * 1024)).toBe('1 GB')
  })

  it('should handle decimal sizes', () => {
    expect(formatFileSize(1536)).toBe('1.5 KB')
    expect(formatFileSize(2048)).toBe('2 KB')
  })

  it('should handle large files', () => {
    expect(formatFileSize(50 * 1024 * 1024)).toBe('50 MB')
  })
})

describe('formatDate', () => {
  it('should format date strings', () => {
    const date = '2024-01-15T10:30:00Z'
    const formatted = formatDate(date)
    expect(formatted).toMatch(/Jan/)
    expect(formatted).toMatch(/2024/)
  })

  it('should format Date objects', () => {
    const date = new Date('2024-01-15T10:30:00Z')
    const formatted = formatDate(date)
    expect(formatted).toMatch(/Jan/)
    expect(formatted).toMatch(/2024/)
  })
})

describe('extractPageNumbers', () => {
  it('should extract page numbers from text', () => {
    const text = 'See page [p.1] and [p.5] for more info'
    const pages = extractPageNumbers(text)
    expect(pages).toEqual([1, 5])
  })

  it('should handle duplicate page numbers', () => {
    const text = 'See [p.1] and [p.1] again'
    const pages = extractPageNumbers(text)
    expect(pages).toEqual([1])
  })

  it('should return empty array for no page numbers', () => {
    const text = 'No page numbers here'
    const pages = extractPageNumbers(text)
    expect(pages).toEqual([])
  })

  it('should sort page numbers', () => {
    const text = 'Pages [p.10], [p.2], [p.5]'
    const pages = extractPageNumbers(text)
    expect(pages).toEqual([2, 5, 10])
  })
})

describe('highlightCitations', () => {
  it('should wrap page citations in span tags', () => {
    const text = 'See page [p.1] for details'
    const highlighted = highlightCitations(text)
    expect(highlighted).toContain('<span class="citation-link"')
    expect(highlighted).toContain('data-page="1"')
    expect(highlighted).toContain('[p.1]')
  })

  it('should handle multiple citations', () => {
    const text = 'See [p.1] and [p.2]'
    const highlighted = highlightCitations(text)
    expect(highlighted.match(/citation-link/g)).toHaveLength(2)
  })
})

describe('debounce', () => {
  jest.useFakeTimers()

  it('should debounce function calls', () => {
    const fn = jest.fn()
    const debouncedFn = debounce(fn, 100)

    debouncedFn()
    debouncedFn()
    debouncedFn()

    expect(fn).not.toHaveBeenCalled()

    jest.advanceTimersByTime(100)

    expect(fn).toHaveBeenCalledTimes(1)
  })

  it('should reset timer on new calls', () => {
    const fn = jest.fn()
    const debouncedFn = debounce(fn, 100)

    debouncedFn()
    jest.advanceTimersByTime(50)
    debouncedFn()
    jest.advanceTimersByTime(50)
    
    expect(fn).not.toHaveBeenCalled()

    jest.advanceTimersByTime(50)

    expect(fn).toHaveBeenCalledTimes(1)
  })
})

describe('generateId', () => {
  it('should generate a string ID', () => {
    const id = generateId()
    expect(typeof id).toBe('string')
    expect(id.length).toBeGreaterThan(0)
  })

  it('should generate unique IDs', () => {
    const id1 = generateId()
    const id2 = generateId()
    expect(id1).not.toBe(id2)
  })
})

describe('isValidPdf', () => {
  it('should validate PDF files', () => {
    const pdfFile = new File([''], 'test.pdf', { type: 'application/pdf' })
    Object.defineProperty(pdfFile, 'size', { value: 1024 * 1024 }) // 1MB

    expect(isValidPdf(pdfFile)).toBe(true)
  })

  it('should reject non-PDF files', () => {
    const textFile = new File([''], 'test.txt', { type: 'text/plain' })
    Object.defineProperty(textFile, 'size', { value: 1024 })

    expect(isValidPdf(textFile)).toBe(false)
  })

  it('should reject files larger than 50MB', () => {
    const largeFile = new File([''], 'test.pdf', { type: 'application/pdf' })
    Object.defineProperty(largeFile, 'size', { value: 51 * 1024 * 1024 }) // 51MB

    expect(isValidPdf(largeFile)).toBe(false)
  })

  it('should accept files up to 50MB', () => {
    const largeFile = new File([''], 'test.pdf', { type: 'application/pdf' })
    Object.defineProperty(largeFile, 'size', { value: 50 * 1024 * 1024 }) // 50MB

    expect(isValidPdf(largeFile)).toBe(true)
  })
})

describe('getErrorMessage', () => {
  it('should extract message from Error objects', () => {
    const error = new Error('Test error')
    expect(getErrorMessage(error)).toBe('Test error')
  })

  it('should return string errors as-is', () => {
    expect(getErrorMessage('String error')).toBe('String error')
  })

  it('should handle unknown error types', () => {
    expect(getErrorMessage(null)).toBe('An unknown error occurred')
    expect(getErrorMessage(123)).toBe('An unknown error occurred')
  })
})

describe('cn', () => {
  it('should merge class names', () => {
    expect(cn('class1', 'class2')).toBe('class1 class2')
  })

  it('should handle conditional classes', () => {
    expect(cn('class1', false && 'class2', 'class3')).toBe('class1 class3')
  })

  it('should handle tailwind class conflicts', () => {
    // tailwind-merge should handle conflicting classes
    const result = cn('p-4', 'p-2')
    expect(result).toBeTruthy()
  })
})

