'use client'

import React from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { Quiz } from '@/components/Quiz'
import { Button } from '@/components/ui/button'
import { ArrowLeft, MessageSquare, FileText } from 'lucide-react'

export default function QuizPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const docId = searchParams.get('docId') || undefined

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border">
        <div className="container mx-auto px-6 py-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link
                href="/"
                className="inline-flex items-center text-xs uppercase tracking-[0.2em] text-muted-foreground hover:text-foreground transition-colors"
              >
                <ArrowLeft className="h-3.5 w-3.5 mr-2" />
                Home
              </Link>
              <span className="text-border">/</span>
              <h1 className="text-sm font-medium tracking-[0.2em] uppercase">Quiz</h1>
            </div>
            <div className="flex items-center gap-2">
              <Link href="/upload">
                <Button variant="outline" size="sm">
                  <FileText className="h-4 w-4 mr-2" />
                  Upload
                </Button>
              </Link>
              <Link href="/chat">
                <Button variant="outline" size="sm">
                  <MessageSquare className="h-4 w-4 mr-2" />
                  Chat
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8">
            <h2 className="text-2xl md:text-3xl mb-2">
              <span className="text-muted-foreground">Test your</span>{' '}
              <span className="font-medium">knowledge</span>
            </h2>
            <p className="text-muted-foreground">
              Generate custom quizzes from your uploaded documents
            </p>
          </div>

          <Quiz docId={docId} />
        </div>
      </main>
    </div>
  )
}
