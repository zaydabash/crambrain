/**
 * Unit tests for FileDrop component
 */

import React from 'react'
import { render, screen, waitFor, fireEvent, act } from '@testing-library/react'
import { FileDrop } from '@/components/FileDrop'
import { apiClient } from '@/lib/api'

// Mock the API client used for polling processing status
jest.mock('@/lib/api', () => ({
  apiClient: {
    getUploadStatus: jest.fn(),
  },
}))

// Mock react-dropzone to bypass native accept/reject behavior and directly trigger onDrop
jest.mock('react-dropzone', () => ({
  useDropzone: (opts: any) => ({
    getRootProps: () => ({ role: 'presentation', tabIndex: 0 }),
    getInputProps: () => ({
      accept: { 'application/pdf': ['.pdf'] },
      onChange: (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = Array.from(e.target.files || [])
        opts.onDrop?.(files)
      },
      type: 'file',
    }),
    isDragActive: false,
  }),
}))

// Mock the API
global.fetch = jest.fn()

function createMockXHR(success = true, responseText = '{"doc_id":"test-doc"}', status = 200) {
  return class {
    upload = { onprogress: jest.fn() }
    onload: (() => void) | null = null
    onerror: (() => void) | null = null
    onabort: (() => void) | null = null
    status = status
    responseText = responseText
    open = jest.fn()
    setRequestHeader = jest.fn()
    send = jest.fn(() => {
      if (success) {
        this.onload && this.onload()
      } else {
        this.onerror && this.onerror()
      }
    })
    abort = jest.fn(() => {
      this.onabort && this.onabort()
    })
  } as any
}

describe('FileDrop', () => {
  const mockOnUploadComplete = jest.fn()
  const mockOnError = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
    ;(global.fetch as jest.Mock).mockClear()
    // Default XHR mock to succeed
    // @ts-ignore
    global.XMLHttpRequest = createMockXHR(true)
  })

  it('should render upload area', () => {
    render(<FileDrop onUploadComplete={mockOnUploadComplete} onError={mockOnError} />)
    
    expect(screen.getByText(/upload your study materials/i)).toBeInTheDocument()
    expect(screen.getByText(/drag and drop a pdf file/i)).toBeInTheDocument()
  })

  it('should show file name when file is selected', async () => {
    render(<FileDrop onUploadComplete={mockOnUploadComplete} onError={mockOnError} />)
    
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' })
    Object.defineProperty(file, 'size', { value: 1024 * 1024 }) // 1MB

    const input = screen.getByTestId('file-input') as HTMLInputElement
    fireEvent.change(input, { target: { files: [file] } })

    await waitFor(() => {
      expect(screen.getByText('test.pdf')).toBeInTheDocument()
    })
  })

  it('should reject non-PDF files', async () => {
    render(<FileDrop onUploadComplete={mockOnUploadComplete} onError={mockOnError} />)
    
    const file = new File(['test content'], 'test.txt', { type: 'text/plain' })
    Object.defineProperty(file, 'size', { value: 1024 })

    const input = screen.getByTestId('file-input') as HTMLInputElement
    fireEvent.change(input, { target: { files: [file] } })

    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith('Please upload a valid PDF file (max 50MB)')
    })
  })

  it('should reject files larger than 50MB', async () => {
    render(<FileDrop onUploadComplete={mockOnUploadComplete} onError={mockOnError} />)
    
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' })
    Object.defineProperty(file, 'size', { value: 51 * 1024 * 1024 }) // 51MB

    const input = screen.getByTestId('file-input') as HTMLInputElement
    fireEvent.change(input, { target: { files: [file] } })

    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith('Please upload a valid PDF file (max 50MB)')
    })
  })

  it('should show a processing state and complete once the backend finishes', async () => {
    jest.useFakeTimers()
    // @ts-ignore
    global.XMLHttpRequest = createMockXHR(true, '{"doc_id":"test-doc","status":"processing"}')
    ;(apiClient.getUploadStatus as jest.Mock).mockResolvedValue({
      doc_id: 'test-doc',
      status: 'ready',
      pages: 2,
      chunks: 5,
    })

    render(<FileDrop onUploadComplete={mockOnUploadComplete} onError={mockOnError} />)

    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' })
    Object.defineProperty(file, 'size', { value: 1024 * 1024 })

    const input = screen.getByTestId('file-input') as HTMLInputElement
    fireEvent.change(input, { target: { files: [file] } })

    await waitFor(() => {
      expect(screen.getByText(/processing document/i)).toBeInTheDocument()
    })

    await act(async () => {
      jest.advanceTimersByTime(3000)
    })

    await waitFor(() => {
      expect(mockOnUploadComplete).toHaveBeenCalledWith('test-doc', 'test.pdf')
    })

    jest.useRealTimers()
  })

  it('should surface a backend processing failure via onError', async () => {
    jest.useFakeTimers()
    // @ts-ignore
    global.XMLHttpRequest = createMockXHR(true, '{"doc_id":"test-doc","status":"processing"}')
    ;(apiClient.getUploadStatus as jest.Mock).mockResolvedValue({
      doc_id: 'test-doc',
      status: 'failed',
      error: 'PDF parsing failed',
    })

    render(<FileDrop onUploadComplete={mockOnUploadComplete} onError={mockOnError} />)

    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' })
    Object.defineProperty(file, 'size', { value: 1024 * 1024 })

    const input = screen.getByTestId('file-input') as HTMLInputElement
    fireEvent.change(input, { target: { files: [file] } })

    await waitFor(() => {
      expect(screen.getByText(/processing document/i)).toBeInTheDocument()
    })

    await act(async () => {
      jest.advanceTimersByTime(3000)
    })

    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith('PDF parsing failed')
    })

    jest.useRealTimers()
  })

  // Note: Integration tests for actual upload would require mocking XMLHttpRequest
  // and the backend API, which is more complex and better suited for E2E tests
})

