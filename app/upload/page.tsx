'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import { FileDrop } from '@/components/FileDrop'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Upload, ArrowLeft, CheckCircle } from 'lucide-react'
import Link from 'next/link'
import { toast } from 'sonner'

export default function UploadPage() {
  const router = useRouter()
  const [uploadedDocs, setUploadedDocs] = useState<Array<{ docId: string; filename: string }>>([])

  const handleUploadComplete = (docId: string, filename: string) => {
    setUploadedDocs(prev => [...prev, { docId, filename }])
    toast.success(`Successfully uploaded and processed ${filename}`)
  }

  const handleError = (error: string) => {
    toast.error(error)
  }

  const handleContinue = () => {
    if (uploadedDocs.length > 0) {
      router.push('/chat')
    }
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/">
                <Button variant="ghost" size="sm">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Home
                </Button>
              </Link>
              <h1 className="text-2xl font-bold">Upload Documents</h1>
            </div>
            <Link href="/chat">
              <Button variant="outline">Go to Chat</Button>
            </Link>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto space-y-8">
          {/* Upload Section */}
          <div>
            <h2 className="text-3xl font-bold mb-2">Upload Your Study Materials</h2>
            <p className="text-muted-foreground mb-8">
              Upload PDF documents to start asking questions and generating quizzes
            </p>
            
            <FileDrop
              onUploadComplete={handleUploadComplete}
              onError={handleError}
            />
          </div>

          {/* Uploaded Documents */}
          {uploadedDocs.length > 0 && (
            <div>
              <h3 className="text-xl font-semibold mb-4">Uploaded Documents</h3>
              <div className="grid gap-4">
                {uploadedDocs.map((doc, index) => (
                  <Card key={doc.docId}>
                    <CardContent className="p-4">
                      <div className="flex items-center space-x-3">
                        <CheckCircle className="h-5 w-5 text-green-500" />
                        <div className="flex-1">
                          <p className="font-medium">{doc.filename}</p>
                          <p className="text-sm text-muted-foreground">
                            Document ID: {doc.docId}
                          </p>
                        </div>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => router.push(`/docs/${doc.docId}`)}
                        >
                          View Document
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {/* Continue Button */}
          {uploadedDocs.length > 0 && (
            <div className="text-center">
              <Button size="lg" onClick={handleContinue}>
                <Upload className="mr-2 h-5 w-5" />
                Continue to Chat ({uploadedDocs.length} document{uploadedDocs.length > 1 ? 's' : ''} ready)
              </Button>
            </div>
          )}

          {/* Instructions */}
          <Card>
            <CardHeader>
              <CardTitle>How to Upload</CardTitle>
              <CardDescription>
                Follow these steps to upload your study materials
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid md:grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center mx-auto mb-2 text-sm font-bold">
                    1
                  </div>
                  <h4 className="font-medium mb-1">Choose File</h4>
                  <p className="text-sm text-muted-foreground">
                    Select a PDF file from your computer
                  </p>
                </div>
                <div className="text-center">
                  <div className="w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center mx-auto mb-2 text-sm font-bold">
                    2
                  </div>
                  <h4 className="font-medium mb-1">Upload & Process</h4>
                  <p className="text-sm text-muted-foreground">
                    File is uploaded and processed by AI
                  </p>
                </div>
                <div className="text-center">
                  <div className="w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center mx-auto mb-2 text-sm font-bold">
                    3
                  </div>
                  <h4 className="font-medium mb-1">Start Studying</h4>
                  <p className="text-sm text-muted-foreground">
                    Ask questions and generate quizzes
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}
