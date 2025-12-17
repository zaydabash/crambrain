'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Chat } from '@/components/Chat'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { ArrowLeft, MessageSquare, FileText, BookOpen } from 'lucide-react'
import { apiClient, type Citation as CitationType } from '@/lib/api'
import { toast } from 'sonner'
import { CHAT_CONSTANTS } from '@/lib/constants'

export default function ChatPage() {
  const router = useRouter()
  const [selectedCitation, setSelectedCitation] = useState<CitationType | null>(null)

  const handleCitationClick = (citation: CitationType) => {
    setSelectedCitation(citation)
    // Navigate to document viewer
    router.push(`/docs/${citation.doc_id}?page=${citation.page}&highlight=${citation.bbox_id}`)
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
              <h1 className="text-2xl font-bold">Study Chat</h1>
            </div>
            <div className="flex items-center space-x-2">
              <Link href="/upload">
                <Button variant="outline" size="sm">
                  <FileText className="h-4 w-4 mr-2" />
                  Upload
                </Button>
              </Link>
              <Link href="/quiz">
                <Button variant="outline" size="sm">
                  <BookOpen className="h-4 w-4 mr-2" />
                  Quiz
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <div className="grid lg:grid-cols-3 gap-8">
            {/* Chat Section */}
            <div className="lg:col-span-2">
              <Chat
                onCitationClick={handleCitationClick}
              />
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Quick Actions */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Quick Actions</CardTitle>
                  <CardDescription>
                    Common study tasks
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-2">
                  <Button
                    variant="outline"
                    className="w-full justify-start"
                    onClick={() => {
                      toast.info(CHAT_CONSTANTS.QUICK_ACTIONS.ASK_TOPICS.TOAST)
                    }}
                  >
                    <MessageSquare className="h-4 w-4 mr-2" />
                    {CHAT_CONSTANTS.QUICK_ACTIONS.ASK_TOPICS.LABEL}
                  </Button>
                  <Button
                    variant="outline"
                    className="w-full justify-start"
                    onClick={() => {
                      toast.info(CHAT_CONSTANTS.QUICK_ACTIONS.EXPLAIN_CONCEPTS.TOAST)
                    }}
                  >
                    <MessageSquare className="h-4 w-4 mr-2" />
                    {CHAT_CONSTANTS.QUICK_ACTIONS.EXPLAIN_CONCEPTS.LABEL}
                  </Button>
                  <Button
                    variant="outline"
                    className="w-full justify-start"
                    onClick={() => {
                      toast.info(CHAT_CONSTANTS.QUICK_ACTIONS.FIND_DEFINITIONS.TOAST)
                    }}
                  >
                    <MessageSquare className="h-4 w-4 mr-2" />
                    {CHAT_CONSTANTS.QUICK_ACTIONS.FIND_DEFINITIONS.LABEL}
                  </Button>
                </CardContent>
              </Card>

              {/* Tips */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Study Tips</CardTitle>
                  <CardDescription>
                    Get the most out of CramBrain
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  {CHAT_CONSTANTS.TIPS.map((tip, index) => (
                    <div key={index} className="text-sm">
                      <p className="font-medium mb-1">{tip.TITLE}</p>
                      <p className="text-muted-foreground">
                        {tip.DESCRIPTION}
                      </p>
                    </div>
                  ))}
                </CardContent>
              </Card>

              {/* Recent Citations */}
              {selectedCitation && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Selected Source</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <p className="text-sm font-medium">
                        Page {selectedCitation.page}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {selectedCitation.quote}
                      </p>
                      <Button
                        variant="outline"
                        size="sm"
                        className="w-full"
                        onClick={() => handleCitationClick(selectedCitation)}
                      >
                        View in Document
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
