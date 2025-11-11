import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

export function formatDate(date: string | Date): string {
  const d = new Date(date)
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function extractPageNumbers(text: string): number[] {
  const pagePattern = /\[p\.(\d+)\]/g
  const matches = text.matchAll(pagePattern)
  const pages = new Set<number>()
  
  for (const match of matches) {
    pages.add(parseInt(match[1]))
  }
  
  return Array.from(pages).sort((a, b) => a - b)
}

export function highlightCitations(text: string): string {
  return text.replace(
    /\[p\.(\d+)\]/g,
    '<span class="citation-link" data-page="$1">[p.$1]</span>'
  )
}

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}

export function generateId(): string {
  return Math.random().toString(36).substr(2, 9)
}

export function isValidPdf(file: File): boolean {
  return file.type === 'application/pdf' && file.size <= 50 * 1024 * 1024 // 50MB
}

export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message
  }
  if (typeof error === 'string') {
    return error
  }
  return 'An unknown error occurred'
}
