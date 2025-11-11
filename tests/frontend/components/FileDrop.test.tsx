/**
 * Unit tests for FileDrop component
 */

import React from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { FileDrop } from '@/components/FileDrop'

// Mock the API
global.fetch = jest.fn()

describe('FileDrop', () => {
  const mockOnUploadComplete = jest.fn()
  const mockOnError = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
    ;(global.fetch as jest.Mock).mockClear()
  })

  it('should render upload area', () => {
    render(<FileDrop onUploadComplete={mockOnUploadComplete} onError={mockOnError} />)
    
    expect(screen.getByText(/upload your study materials/i)).toBeInTheDocument()
    expect(screen.getByText(/drag and drop a pdf file/i)).toBeInTheDocument()
  })

  it('should show file name when file is selected', async () => {
    const user = userEvent.setup()
    render(<FileDrop onUploadComplete={mockOnUploadComplete} onError={mockOnError} />)
    
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' })
    Object.defineProperty(file, 'size', { value: 1024 * 1024 }) // 1MB

    const input = screen.getByRole('textbox', { hidden: true }) as HTMLInputElement
    await user.upload(input, file)

    await waitFor(() => {
      expect(screen.getByText('test.pdf')).toBeInTheDocument()
    })
  })

  it('should reject non-PDF files', async () => {
    const user = userEvent.setup()
    render(<FileDrop onUploadComplete={mockOnUploadComplete} onError={mockOnError} />)
    
    const file = new File(['test content'], 'test.txt', { type: 'text/plain' })
    Object.defineProperty(file, 'size', { value: 1024 })

    const input = screen.getByRole('textbox', { hidden: true }) as HTMLInputElement
    await user.upload(input, file)

    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith('Please upload a valid PDF file (max 50MB)')
    })
  })

  it('should reject files larger than 50MB', async () => {
    const user = userEvent.setup()
    render(<FileDrop onUploadComplete={mockOnUploadComplete} onError={mockOnError} />)
    
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' })
    Object.defineProperty(file, 'size', { value: 51 * 1024 * 1024 }) // 51MB

    const input = screen.getByRole('textbox', { hidden: true }) as HTMLInputElement
    await user.upload(input, file)

    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith('Please upload a valid PDF file (max 50MB)')
    })
  })

  // Note: Integration tests for actual upload would require mocking XMLHttpRequest
  // and the backend API, which is more complex and better suited for E2E tests
})

