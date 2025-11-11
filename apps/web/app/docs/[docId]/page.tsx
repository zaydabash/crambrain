'use client'

import React, { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { PdfViewer } from '@/components/PdfViewer'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ArrowLeft, FileText, ExternalLink } from 'lucide-react'
import { apiClient, type DocumentMetadata } from '@/lib/api'
import { toast } from 'sonner'

interface DocumentPageProps {
  params: {
    docId: string
  }
}

export default function DocumentPage({ params }: DocumentPageProps) {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [document, setDocument] = useState<DocumentMetadata | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const currentPage = parseInt(searchParams.get('page') || '1')
  const highlightBboxId = searchParams.get('highlight') || undefined

  useEffect(() => {
    const fetchDocument = async () => {
      try {
        const doc = await apiClient.getDocument(params.docId)
        setDocument(doc)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load document')
        toast.error('Failed to load document')
      } finally {
        setLoading(false)
      }
    }

    fetchDocument()
  }, [params.docId])

  const handlePageChange = (page: number) => {
    const url = new URL(window.location.href)
    url.searchParams.set('page', page.toString())
    if (highlightBboxId) {
      url.searchParams.set('highlight', highlightBboxId)
    }
    router.push(url.pathname + url.search)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <header className="border-b">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center space-x-4">
              <Link href="/chat">
                <Button variant="ghost" size="sm">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Chat
                </Button>
              </Link>
              <h1 className="text-2xl font-bold">Loading Document...</h1>
            </div>
          </div>
        </header>
        <main className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-center h-96">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4" />
              <p className="text-muted-foreground">Loading document...</p>
            </div>
          </div>
        </main>
      </div>
    )
  }

  if (error || !document) {
    return (
      <div className="min-h-screen bg-background">
        <header className="border-b">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center space-x-4">
              <Link href="/chat">
                <Button variant="ghost" size="sm">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Chat
                </Button>
              </Link>
              <h1 className="text-2xl font-bold">Document Error</h1>
            </div>
          </div>
        </header>
        <main className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-center h-96">
            <div className="text-center">
              <p className="text-destructive mb-2">Failed to load document</p>
              <p className="text-sm text-muted-foreground mb-4">{error}</p>
              <Link href="/chat">
                <Button>Back to Chat</Button>
              </Link>
            </div>
          </div>
        </main>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/chat">
                <Button variant="ghost" size="sm">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Chat
                </Button>
              </Link>
              <div>
                <h1 className="text-xl font-bold">{document.original_name}</h1>
                <p className="text-sm text-muted-foreground">
                  {document.pages} pages • {document.chunks} chunks
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => window.open(document.file_url, '_blank')}
              >
                <ExternalLink className="h-4 w-4 mr-2" />
                Open Original
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <div className="grid lg:grid-cols-4 gap-8">
            {/* PDF Viewer */}
            <div className="lg:col-span-3">
              <PdfViewer
                fileUrl={document.file_url}
                currentPage={currentPage}
                highlightBboxId={highlightBboxId}
                onPageChange={handlePageChange}
              />
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Document Info */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Document Info</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="text-sm">
                    <p className="font-medium">Filename</p>
                    <p className="text-muted-foreground">{document.original_name}</p>
                  </div>
                  <div className="text-sm">
                    <p className="font-medium">Pages</p>
                    <p className="text-muted-foreground">{document.pages}</p>
                  </div>
                  <div className="text-sm">
                    <p className="font-medium">Chunks</p>
                    <p className="text-muted-foreground">{document.chunks}</p>
                  </div>
                  <div className="text-sm">
                    <p className="font-medium">Uploaded</p>
                    <p className="text-muted-foreground">
                      {new Date(document.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </CardContent>
              </Card>

              {/* Page Thumbnails */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Pages</CardTitle>
                  <CardDescription>
                    Click to jump to a page
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-2">
                    {document.preview_urls.map((url, index) => (
                      <button
                        key={index}
                        className={`p-2 border rounded text-sm hover:bg-accent transition-colors ${
                          currentPage === index + 1 ? 'bg-primary text-primary-foreground' : ''
                        }`}
                        onClick={() => handlePageChange(index + 1)}
                      >
                        <img
                          src={url}
                          alt={`Page ${index + 1}`}
                          className="w-full h-20 object-cover rounded mb-1"
                        />
                        Page {index + 1}
                      </button>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Actions */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Actions</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <Button
                    variant="outline"
                    className="w-full justify-start"
                    onClick={() => router.push(`/chat?docId=${document.doc_id}`)}
                  >
                    <FileText className="h-4 w-4 mr-2" />
                    Ask Questions
                  </Button>
                  <Button
                    variant="outline"
                    className="w-full justify-start"
                    onClick={() => router.push(`/quiz?docId=${document.doc_id}`)}
                  >
                    <FileText className="h-4 w-4 mr-2" />
                    Generate Quiz
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
