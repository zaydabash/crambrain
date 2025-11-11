"use client"

import React, { useState } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  BookOpen, 
  Image, 
  Table, 
  ExternalLink, 
  Eye,
  Copy,
  Check,
  ChevronDown,
  ChevronUp,
  FileText
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { type Citation as CitationType } from '@/lib/api'

interface CitationProps {
  citation: CitationType
  onClick: (citation: CitationType) => void
  onPageClick?: (page: number, bbox?: [number, number, number, number]) => void
  onSourceClick?: (url: string) => void
  showThumbnail?: boolean
  expanded?: boolean
  className?: string
}

export function Citation({
  citation,
  onClick,
  onPageClick,
  onSourceClick,
  showThumbnail = true,
  expanded = false,
  className
}: CitationProps) {
  const [isExpanded, setIsExpanded] = useState(expanded)
  const [copied, setCopied] = useState(false)

  const getCitationIcon = (chunkType?: string) => {
    switch (chunkType) {
      case 'image': return <Image className="h-4 w-4" />
      case 'table': return <Table className="h-4 w-4" />
      default: return <BookOpen className="h-4 w-4" />
    }
  }

  const getCitationColor = (chunkType?: string): string => {
    switch (chunkType) {
      case 'image': return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'table': return 'bg-green-100 text-green-800 border-green-200'
      default: return 'bg-orange-100 text-orange-800 border-orange-200'
    }
  }

  const getScoreColor = (score?: number): string => {
    if (!score) return 'text-gray-600'
    if (score >= 0.8) return 'text-green-600'
    if (score >= 0.6) return 'text-yellow-600'
    return 'text-red-600'
  }

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(citation.quote)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy text:', err)
    }
  }

  const handlePageClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    onPageClick?.(citation.page)
  }

  const handleSourceClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (citation.source_url) {
      onSourceClick?.(citation.source_url)
    }
  }

  const handleCardClick = () => {
    onClick(citation)
  }

  const truncatedText = citation.quote.length > 200 
    ? citation.quote.substring(0, 200) + '...'
    : citation.quote

  return (
    <Card 
      className={cn(
        "w-full transition-all duration-200 hover:shadow-md cursor-pointer",
        className
      )}
      onClick={handleCardClick}
    >
      <CardContent className="p-4">
        <div className="flex items-start space-x-3">
          {/* Thumbnail */}
          {showThumbnail && (
            <div className="flex-shrink-0">
              {citation.preview_url ? (
                <img
                  src={citation.preview_url}
                  alt={`Page ${citation.page} thumbnail`}
                  className="w-16 h-20 object-cover rounded border shadow-sm cursor-pointer hover:shadow-md transition-shadow"
                  onClick={handlePageClick}
                />
              ) : (
                <div 
                  className="w-16 h-20 bg-gray-100 border rounded flex items-center justify-center cursor-pointer hover:bg-gray-200 transition-colors"
                  onClick={handlePageClick}
                >
                  <div className="text-center">
                    <div className="text-xs font-medium text-gray-600">Page</div>
                    <div className="text-lg font-bold text-gray-800">{citation.page}</div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Content */}
          <div className="flex-1 min-w-0">
            {/* Header */}
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <Badge 
                  variant="outline" 
                  className={cn("text-xs", getCitationColor())}
                >
                  {getCitationIcon()}
                  <span className="ml-1">text</span>
                </Badge>
                
                <Badge variant="secondary" className="text-xs">
                  Page {citation.page}
                </Badge>
                
                {citation.score && (
                  <span className={cn("text-xs font-medium", getScoreColor(citation.score))}>
                    {Math.round(citation.score * 100)}% match
                  </span>
                )}
              </div>

              <div className="flex items-center space-x-1">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation()
                    copyToClipboard()
                  }}
                  className="h-6 w-6 p-0"
                >
                  {copied ? (
                    <Check className="h-3 w-3 text-green-600" />
                  ) : (
                    <Copy className="h-3 w-3" />
                  )}
                </Button>
                
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation()
                    setIsExpanded(!isExpanded)
                  }}
                  className="h-6 w-6 p-0"
                >
                  {isExpanded ? (
                    <ChevronUp className="h-3 w-3" />
                  ) : (
                    <ChevronDown className="h-3 w-3" />
                  )}
                </Button>
              </div>
            </div>

            {/* Text Content */}
            <div className="space-y-2">
              <p className="text-sm text-gray-800 leading-relaxed">
                {isExpanded ? citation.quote : truncatedText}
              </p>
              
              {citation.quote.length > 200 && !isExpanded && (
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    setIsExpanded(true)
                  }}
                  className="text-xs text-blue-600 hover:text-blue-800 font-medium"
                >
                  Show more
                </button>
              )}
            </div>

            {/* Actions */}
            <div className="flex items-center space-x-2 mt-3">
              <Button
                variant="outline"
                size="sm"
                onClick={handlePageClick}
                className="h-7 text-xs"
              >
                <Eye className="h-3 w-3 mr-1" />
                View Page
              </Button>
              
              {citation.source_url && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleSourceClick}
                  className="h-7 text-xs"
                >
                  <ExternalLink className="h-3 w-3 mr-1" />
                  Source
                </Button>
              )}
            </div>

            {/* Metadata */}
            <div className="mt-2 text-xs text-gray-500">
              <span>Doc ID: {citation.doc_id}</span>
              {citation.chunk_id && (
                <span className="ml-2">Chunk: {citation.chunk_id}</span>
              )}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

// Citation List Component
interface CitationListProps {
  citations: CitationType[]
  onCitationClick?: (citation: CitationType) => void
  onPageClick?: (page: number, bbox?: [number, number, number, number]) => void
  onSourceClick?: (url: string) => void
  showThumbnails?: boolean
  className?: string
}

export function CitationList({
  citations,
  onCitationClick,
  onPageClick,
  onSourceClick,
  showThumbnails = true,
  className
}: CitationListProps) {
  if (!citations.length) {
    return (
      <div className={cn("text-center py-8 text-gray-500", className)}>
        <BookOpen className="h-8 w-8 mx-auto mb-2 text-gray-400" />
        <p>No citations available</p>
      </div>
    )
  }

  return (
    <div className={cn("space-y-3", className)}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Citations</h3>
        <Badge variant="secondary">
          {citations.length} citation{citations.length !== 1 ? 's' : ''}
        </Badge>
      </div>
      
      {citations.map((citation, index) => (
        <Citation
          key={`${citation.doc_id}-${citation.page}-${index}`}
          citation={citation}
          onClick={onCitationClick || (() => {})}
          onPageClick={onPageClick}
          onSourceClick={onSourceClick}
          showThumbnail={showThumbnails}
        />
      ))}
    </div>
  )
}
