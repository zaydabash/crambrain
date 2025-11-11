"use client"

import React, { useState, useEffect, useRef, useCallback } from 'react'
import { Document, Page, pdfjs } from 'react-pdf'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  ChevronLeft, 
  ChevronRight, 
  ZoomIn, 
  ZoomOut, 
  RotateCw,
  Download,
  ExternalLink,
  Eye,
  EyeOff,
  BookOpen,
  Image,
  Table
} from 'lucide-react'
import { cn } from '@/lib/utils'

// Configure PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.js`

interface Citation {
  page: number
  text: string
  score: number
  chunk_id: string
  bbox?: [number, number, number, number]
  chunk_type: string
  preview_url?: string
  source_url?: string
}

interface PdfViewerProps {
  fileUrl: string
  docId: string
  citations?: Citation[]
  onPageClick?: (page: number, bbox?: [number, number, number, number]) => void
  onCitationClick?: (citation: Citation) => void
  highlightCitations?: boolean
  showThumbnails?: boolean
  className?: string
}

interface PageHighlight {
  page: number
  bbox: [number, number, number, number]
  color: string
  opacity: number
  citation: Citation
}

export function PdfViewer({
  fileUrl,
  docId,
  citations = [],
  onPageClick,
  onCitationClick,
  highlightCitations = true,
  showThumbnails = true,
  className
}: PdfViewerProps) {
  const [numPages, setNumPages] = useState<number>(0)
  const [currentPage, setCurrentPage] = useState<number>(1)
  const [scale, setScale] = useState<number>(1.2)
  const [rotation, setRotation] = useState<number>(0)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [pageHighlights, setPageHighlights] = useState<PageHighlight[]>([])
  const [showThumbnailPanel, setShowThumbnailPanel] = useState<boolean>(showThumbnails)
  const [pageDimensions, setPageDimensions] = useState<{[key: number]: {width: number, height: number}}>({})
  
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  // Generate highlights from citations
  useEffect(() => {
    if (!highlightCitations || !citations.length) {
      setPageHighlights([])
      return
    }

    const highlights: PageHighlight[] = citations.map((citation, index) => ({
      page: citation.page,
      bbox: citation.bbox || [0, 0, 100, 20], // Default bbox if not provided
      color: getCitationColor(citation.chunk_type),
      opacity: 0.3 + (citation.score * 0.4), // Opacity based on relevance score
      citation
    }))

    setPageHighlights(highlights)
  }, [citations, highlightCitations])

  const getCitationColor = (chunkType: string): string => {
    switch (chunkType) {
      case 'image': return '#3b82f6' // Blue for images
      case 'table': return '#10b981' // Green for tables
      default: return '#f59e0b' // Orange for text
    }
  }

  const getCitationIcon = (chunkType: string) => {
    switch (chunkType) {
      case 'image': return <Image className="h-3 w-3" />
      case 'table': return <Table className="h-3 w-3" />
      default: return <BookOpen className="h-3 w-3" />
    }
  }

  const onDocumentLoadSuccess = useCallback(({ numPages }: { numPages: number }) => {
    setNumPages(numPages)
    setLoading(false)
    setError(null)
  }, [])

  const onDocumentLoadError = useCallback((error: Error) => {
    setError(`Failed to load PDF: ${error.message}`)
    setLoading(false)
  }, [])

  const onPageLoadSuccess = useCallback((page: any) => {
    const { width, height } = page.originalWidth ? 
      { width: page.originalWidth, height: page.originalHeight } :
      { width: page.width, height: page.height }
    
    setPageDimensions(prev => ({
      ...prev,
      [page.pageNumber]: { width, height }
    }))
  }, [])

  const goToPage = (page: number) => {
    if (page >= 1 && page <= numPages) {
      setCurrentPage(page)
    }
  }

  const goToPreviousPage = () => {
    goToPage(currentPage - 1)
  }

  const goToNextPage = () => {
    goToPage(currentPage + 1)
  }

  const zoomIn = () => {
    setScale(prev => Math.min(prev + 0.2, 3.0))
  }

  const zoomOut = () => {
    setScale(prev => Math.max(prev - 0.2, 0.5))
  }

  const rotate = () => {
    setRotation(prev => (prev + 90) % 360)
  }

  const downloadPdf = () => {
    const link = document.createElement('a')
    link.href = fileUrl
    link.download = `document-${docId}.pdf`
    link.click()
  }

  const handlePageClick = (event: React.MouseEvent<HTMLDivElement>) => {
    if (!onPageClick) return

    const rect = event.currentTarget.getBoundingClientRect()
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top
    
    // Convert click coordinates to PDF coordinates
    const pdfX = x / scale
    const pdfY = y / scale
    
    onPageClick(currentPage, [pdfX, pdfY, pdfX + 10, pdfY + 10])
  }

  const renderPageHighlights = (pageNum: number) => {
    const pageHighlightsForPage = pageHighlights.filter(h => h.page === pageNum)
    
    if (!pageHighlightsForPage.length) return null

    return (
      <div className="absolute inset-0 pointer-events-none">
        {pageHighlightsForPage.map((highlight, index) => (
          <div
            key={index}
            className="absolute border-2 border-dashed cursor-pointer"
            style={{
              left: `${highlight.bbox[0]}px`,
              top: `${highlight.bbox[1]}px`,
              width: `${highlight.bbox[2] - highlight.bbox[0]}px`,
              height: `${highlight.bbox[3] - highlight.bbox[1]}px`,
              backgroundColor: `${highlight.color}${Math.round(highlight.opacity * 255).toString(16).padStart(2, '0')}`,
              borderColor: highlight.color,
            }}
            title={`Citation: ${highlight.citation?.text?.substring(0, 100)}...`}
            onClick={() => onCitationClick?.(highlight.citation)}
          />
        ))}
      </div>
    )
  }

  const renderThumbnails = () => {
    if (!showThumbnailPanel) return null

    return (
      <div className="w-32 bg-gray-100 border-r overflow-y-auto max-h-96">
        <div className="p-2 space-y-2">
          {Array.from({ length: numPages }, (_, i) => i + 1).map(pageNum => {
            const pageCitations = citations.filter(c => c.page === pageNum)
            return (
              <div
                key={pageNum}
                className={cn(
                  "cursor-pointer border rounded p-1 relative",
                  currentPage === pageNum ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
                )}
                onClick={() => goToPage(pageNum)}
              >
                <Document
                  file={fileUrl}
                  onLoadSuccess={() => {}}
                  loading={<div className="w-full h-20 bg-gray-200 animate-pulse" />}
                >
                  <Page
                    pageNumber={pageNum}
                    width={100}
                    renderTextLayer={false}
                    renderAnnotationLayer={false}
                  />
                </Document>
                <div className="text-xs text-center mt-1 font-medium">
                  Page {pageNum}
                </div>
                {pageCitations.length > 0 && (
                  <div className="absolute top-1 right-1">
                    <Badge variant="secondary" className="text-xs px-1 py-0">
                      {pageCitations.length}
                    </Badge>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>
    )
  }

  const renderCitationPanel = () => {
    const currentPageCitations = citations.filter(c => c.page === currentPage)
    
    if (!currentPageCitations.length) return null

    return (
      <div className="p-4 border-t bg-gray-50">
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h4 className="font-medium text-sm">Citations on Page {currentPage}</h4>
            <Badge variant="outline">{currentPageCitations.length}</Badge>
          </div>
          
          <div className="space-y-2 max-h-32 overflow-y-auto">
            {currentPageCitations.map((citation, index) => (
              <div
                key={index}
                className="flex items-start space-x-2 p-2 bg-white rounded border cursor-pointer hover:bg-gray-50"
                onClick={() => onCitationClick?.(citation)}
              >
                <div className="flex-shrink-0 mt-0.5">
                  {getCitationIcon(citation.chunk_type)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-xs text-gray-600 mb-1">
                    {citation.chunk_type.toUpperCase()} • Score: {citation.score.toFixed(2)}
                  </div>
                  <div className="text-sm text-gray-800 line-clamp-2">
                    {citation.text.substring(0, 100)}...
                  </div>
                </div>
                <ExternalLink className="h-3 w-3 text-gray-400 flex-shrink-0 mt-1" />
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <Card className={cn("w-full", className)}>
        <CardContent className="flex items-center justify-center h-96">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4" />
            <p className="text-muted-foreground">Loading PDF...</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className={cn("w-full", className)}>
        <CardContent className="flex items-center justify-center h-96">
          <div className="text-center">
            <p className="text-destructive mb-2">Failed to load PDF</p>
            <p className="text-sm text-muted-foreground">{error}</p>
            <Button 
              onClick={() => window.location.reload()} 
              className="mt-4"
              variant="outline"
            >
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={cn("w-full overflow-hidden", className)}>
      <CardContent className="p-0">
        {/* Toolbar */}
        <div className="flex items-center justify-between p-4 border-b bg-muted/50">
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={goToPreviousPage}
              disabled={currentPage <= 1}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            
            <span className="text-sm font-medium">
              Page {currentPage} of {numPages}
            </span>
            
            <Button
              variant="outline"
              size="sm"
              onClick={goToNextPage}
              disabled={currentPage >= numPages}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>

          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={zoomOut}
            >
              <ZoomOut className="h-4 w-4" />
            </Button>
            
            <span className="text-sm font-medium min-w-[60px] text-center">
              {Math.round(scale * 100)}%
            </span>
            
            <Button
              variant="outline"
              size="sm"
              onClick={zoomIn}
            >
              <ZoomIn className="h-4 w-4" />
            </Button>
            
            <Button
              variant="outline"
              size="sm"
              onClick={rotate}
            >
              <RotateCw className="h-4 w-4" />
            </Button>
            
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowThumbnailPanel(!showThumbnailPanel)}
            >
              {showThumbnailPanel ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </Button>
            
            <Button
              variant="outline"
              size="sm"
              onClick={downloadPdf}
            >
              <Download className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* PDF Content */}
        <div className="flex">
          {renderThumbnails()}
          
          <div className="flex-1 overflow-auto">
            <div 
              ref={containerRef}
              className="flex justify-center p-4"
              onClick={handlePageClick}
            >
              <div className="relative">
                <Document
                  file={fileUrl}
                  onLoadSuccess={onDocumentLoadSuccess}
                  onLoadError={onDocumentLoadError}
                  loading={<div className="w-full h-96 bg-gray-200 animate-pulse" />}
                >
                  <Page
                    pageNumber={currentPage}
                    scale={scale}
                    rotate={rotation}
                    onLoadSuccess={onPageLoadSuccess}
                    renderTextLayer={true}
                    renderAnnotationLayer={true}
                    className="shadow-lg"
                  />
                </Document>
                
                {/* Render highlights */}
                {renderPageHighlights(currentPage)}
              </div>
            </div>
          </div>
        </div>

        {/* Citation Panel */}
        {renderCitationPanel()}

        {/* Citation Legend */}
        {citations.length > 0 && (
          <div className="p-4 border-t bg-gray-50">
            <div className="flex items-center space-x-4 text-sm">
              <span className="font-medium">Citation Types:</span>
              <div className="flex items-center space-x-2">
                <Badge variant="outline" className="bg-orange-100 text-orange-800">
                  <BookOpen className="h-3 w-3 mr-1" />
                  Text
                </Badge>
                <Badge variant="outline" className="bg-blue-100 text-blue-800">
                  <Image className="h-3 w-3 mr-1" />
                  Image
                </Badge>
                <Badge variant="outline" className="bg-green-100 text-green-800">
                  <Table className="h-3 w-3 mr-1" />
                  Table
                </Badge>
              </div>
              <span className="text-gray-600">
                {citations.length} total citation{citations.length !== 1 ? 's' : ''}
              </span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}