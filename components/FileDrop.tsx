'use client'

import React, { useCallback, useState, useRef, useEffect } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, X, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { cn, formatFileSize, isValidPdf } from '@/lib/utils'
import { apiClient } from '@/lib/api'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://crambrain-api-v2.onrender.com'
const STATUS_POLL_INTERVAL_MS = 3000

interface FileDropProps {
  onUploadComplete: (docId: string, filename: string) => void
  onError: (error: string) => void
}

export function FileDrop({ onUploadComplete, onError }: FileDropProps) {
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [processing, setProcessing] = useState(false)
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const xhrRef = useRef<XMLHttpRequest | null>(null)
  const pollTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const stopPolling = () => {
    if (pollTimeoutRef.current) {
      clearTimeout(pollTimeoutRef.current)
      pollTimeoutRef.current = null
    }
  }

  useEffect(() => {
    return () => stopPolling()
  }, [])

  const pollUploadStatus = useCallback((docId: string, filename: string) => {
    const poll = async () => {
      try {
        const result = await apiClient.getUploadStatus(docId)
        if (result.status === 'ready') {
          setProcessing(false)
          onUploadComplete(docId, filename)
          return
        }
        if (result.status === 'failed') {
          setProcessing(false)
          onError(result.error || 'Failed to process document')
          return
        }
        pollTimeoutRef.current = setTimeout(poll, STATUS_POLL_INTERVAL_MS)
      } catch (error) {
        setProcessing(false)
        onError(error instanceof Error ? error.message : 'Failed to check processing status')
      }
    }
    pollTimeoutRef.current = setTimeout(poll, STATUS_POLL_INTERVAL_MS)
  }, [onUploadComplete, onError])

  const handleCancel = () => {
    if (xhrRef.current) {
      xhrRef.current.abort()
      xhrRef.current = null
    }
    stopPolling()
    setUploading(false)
    setProcessing(false)
    setUploadProgress(0)
    onError('Upload canceled')
  }

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (!file) return

    if (!isValidPdf(file)) {
      onError('Please upload a valid PDF file (max 50MB)')
      return
    }

    setUploadedFile(file)
    setUploading(true)
    setUploadProgress(0)

    try {
      // Direct upload to backend - handles B2 upload and ingestion in one step
      // Use XHR directly to get reference for cancellation
      const formData = new FormData()
      formData.append('file', file)
      
      const xhr = new XMLHttpRequest()
      xhrRef.current = xhr
      
      // Track upload progress
      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const progress = Math.round((event.loaded / event.total) * 100)
          setUploadProgress(progress)
        }
      }
      
      xhr.onerror = () => {
        setUploading(false)
        setUploadProgress(0)
        onError('Network error during upload')
        xhrRef.current = null
      }
      
      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          let response: { doc_id: string; status: string }
          try {
            response = JSON.parse(xhr.responseText)
          } catch (error) {
            console.error('Failed to parse response:', error)
            onError('Failed to process upload response')
            setUploading(false)
            setUploadProgress(0)
            xhrRef.current = null
            return
          }

          setUploadProgress(100)
          xhrRef.current = null

          if (response.status === 'processing') {
            setUploading(false)
            setProcessing(true)
            pollUploadStatus(response.doc_id, file.name)
            return
          }

          setUploading(false)
          setUploadProgress(0)
          onUploadComplete(response.doc_id, file.name)
        } else {
          try {
            const error = JSON.parse(xhr.responseText)
            onError(error.detail || `Upload failed: ${xhr.status}`)
          } catch {
            onError(`Upload failed: ${xhr.status} ${xhr.statusText}`)
          } finally {
            setUploading(false)
            setUploadProgress(0)
            xhrRef.current = null
          }
        }
      }
      
      xhr.open('POST', `${API_BASE_URL}/v1/upload`)
      xhr.send(formData)
      
    } catch (error) {
      console.error('Upload failed:', error)
      onError(error instanceof Error ? error.message : 'Upload failed')
      setUploading(false)
      setUploadProgress(0)
      xhrRef.current = null
    }
  }, [onUploadComplete, onError, pollUploadStatus])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
    },
    multiple: false,
    disabled: uploading || processing,
  })

  const removeFile = () => {
    setUploadedFile(null)
    setUploadProgress(0)
  }

  return (
    <div className="w-full max-w-2xl mx-auto">
      <Card>
        <CardContent className="p-6">
          {!uploadedFile ? (
            <div
              {...getRootProps()}
              className={cn(
                "border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors",
                isDragActive
                  ? "border-primary bg-primary/5"
                  : "border-muted-foreground/25 hover:border-primary/50",
                (uploading || processing) && "pointer-events-none opacity-50"
              )}
            >
              <input data-testid="file-input" aria-label="file input" {...getInputProps()} />
              <Upload className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
              <div className="space-y-2">
                <h3 className="text-lg font-medium">
                  {isDragActive ? 'Drop your PDF here' : 'Upload your study materials'}
                </h3>
                <p className="text-muted-foreground">
                  Drag and drop a PDF file, or click to browse
                </p>
                <p className="text-sm text-muted-foreground">
                  Maximum file size: 50MB
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
                <div className="flex items-center space-x-3">
                  <FileText className="h-8 w-8 text-primary" />
                  <div>
                    <p className="font-medium">{uploadedFile.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {formatFileSize(uploadedFile.size)}
                    </p>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={removeFile}
                  disabled={uploading || processing}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>

              {uploading && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span>Uploading document...</span>
                    <div className="flex items-center gap-2">
                      <span className="text-muted-foreground">{uploadProgress}%</span>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={handleCancel}
                        className="h-6 px-2 text-xs"
                      >
                        Cancel
                      </Button>
                    </div>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2">
                    <div
                      className="bg-primary h-2 rounded-full transition-all duration-300"
                      style={{ width: `${uploadProgress}%` }}
                    />
                  </div>
                </div>
              )}

              {processing && (
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span>Processing document... this can take a minute for larger files</span>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleCancel}
                    className="h-6 px-2 text-xs"
                  >
                    Cancel
                  </Button>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
