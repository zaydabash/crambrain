'use client'

import React, { useCallback, useState, useRef } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, X, CheckCircle, AlertCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { cn, formatFileSize, isValidPdf } from '@/lib/utils'
import { apiClient } from '@/lib/api'

interface FileDropProps {
  onUploadComplete: (docId: string, filename: string) => void
  onError: (error: string) => void
}

export function FileDrop({ onUploadComplete, onError }: FileDropProps) {
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const xhrRef = useRef<XMLHttpRequest | null>(null)

  const handleCancel = () => {
    if (xhrRef.current) {
      xhrRef.current.abort()
      xhrRef.current = null
      setUploading(false)
      setUploadProgress(0)
      onError('Upload canceled')
    }
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
      // Step 1: Get presigned URL
      setUploadProgress(10)
      const presignResponse = await apiClient.presignUpload(file.name)

      // Step 2: Upload to S3 using XHR for progress tracking
      const xhr = new XMLHttpRequest()
      xhrRef.current = xhr

      // Track upload progress
      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          // Map 10% -> 60% for actual upload (S3/B2 PUT)
          const progress = 10 + Math.round((event.loaded / event.total) * 50)
          setUploadProgress(progress)
        }
      }

      xhr.onerror = (event) => {
        console.error('XHR upload error:', {
          status: xhr.status,
          statusText: xhr.statusText,
          responseText: xhr.responseText,
          readyState: xhr.readyState,
          uploadUrl: presignResponse.upload_url.substring(0, 100) + '...'
        })
        
        let errorMessage = 'Network error during upload'
        if (xhr.status === 0) {
          errorMessage = 'Upload failed: Connection error. Please check your internet connection or CORS configuration.'
        } else if (xhr.status === 403) {
          errorMessage = 'Upload failed: Access denied. The upload URL may have expired or is invalid.'
        } else if (xhr.status >= 400) {
          errorMessage = `Upload failed: ${xhr.status} ${xhr.statusText || 'Unknown error'}`
        }
        
        setUploading(false)
        setUploadProgress(0)
        onError(errorMessage)
        xhrRef.current = null
      }

      xhr.onload = async () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          // Upload successful, now ingest
          setUploadProgress(70)
          
          try {
            const ingestResponse = await apiClient.ingestDocument(
              presignResponse.file_url,
              file.name
            )

            setUploadProgress(100)
            onUploadComplete(ingestResponse.doc_id, file.name)
          } catch (error) {
            console.error('Ingest failed:', error)
            onError(error instanceof Error ? error.message : 'Failed to process document')
          } finally {
            setUploading(false)
            setUploadProgress(0)
            xhrRef.current = null
          }
        } else {
          setUploading(false)
          setUploadProgress(0)
          onError(`Upload failed: ${xhr.status}`)
          xhrRef.current = null
        }
      }

      // Start the PUT request
      xhr.open('PUT', presignResponse.upload_url, true)
      
      // Set Content-Type header (must match what was signed in presigned URL)
      xhr.setRequestHeader('Content-Type', 'application/pdf')
      
      // Log for debugging
      console.log('Starting upload to:', presignResponse.upload_url.substring(0, 100) + '...')
      console.log('File size:', file.size, 'bytes')
      
      xhr.send(file)
      
    } catch (error) {
      console.error('Upload failed:', error)
      onError(error instanceof Error ? error.message : 'Upload failed')
      setUploading(false)
      setUploadProgress(0)
      xhrRef.current = null
    }
  }, [onUploadComplete, onError, xhrRef])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
    },
    multiple: false,
    disabled: uploading,
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
                uploading && "pointer-events-none opacity-50"
              )}
            >
              <input {...getInputProps()} />
              <Upload className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
              <div className="space-y-2">
                <h3 className="text-lg font-semibold">
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
                  disabled={uploading}
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
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
