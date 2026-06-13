'use client'

import React from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { ArrowRight, BookOpen, FileText, MessageSquare, GraduationCap } from 'lucide-react'

const previewColumns = [
  {
    icon: FileText,
    label: '01. Upload',
    title: 'Drop in a PDF',
    description: 'Lecture slides, textbooks, and notes, indexed in seconds.',
  },
  {
    icon: MessageSquare,
    label: '02. Ask',
    title: 'Get a cited answer',
    description: 'Every claim links back to the exact page it came from.',
  },
  {
    icon: GraduationCap,
    label: '03. Quiz',
    title: 'Test yourself',
    description: 'Multiple choice, short answer, and fill-in-the-blank, generated for you.',
  },
]

const steps = [
  {
    number: '01',
    title: 'Upload your PDF',
    description: 'Drag in lecture notes, textbooks, or slides.',
  },
  {
    number: '02',
    title: 'AI indexes the content',
    description: 'Text is extracted, chunked, and embedded for retrieval.',
  },
  {
    number: '03',
    title: 'Ask anything',
    description: 'Get answers with clickable citations back to the source page.',
  },
  {
    number: '04',
    title: 'Quiz yourself',
    description: 'Generate questions from the same material and test your recall.',
  },
]

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border">
        <div className="container mx-auto px-6 py-5 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BookOpen className="h-5 w-5" />
            <span className="text-sm font-medium tracking-[0.2em]">CRAMBRAIN</span>
          </div>
          <nav className="flex items-center gap-8">
            <Link
              href="/upload"
              className="hidden sm:inline text-xs uppercase tracking-[0.2em] text-muted-foreground hover:text-foreground transition-colors"
            >
              Upload
            </Link>
            <Link
              href="/chat"
              className="hidden sm:inline text-xs uppercase tracking-[0.2em] text-muted-foreground hover:text-foreground transition-colors"
            >
              Chat
            </Link>
            <Link
              href="/quiz"
              className="hidden sm:inline text-xs uppercase tracking-[0.2em] text-muted-foreground hover:text-foreground transition-colors"
            >
              Quiz
            </Link>
            <Link href="/chat">
              <Button size="sm">Start studying</Button>
            </Link>
          </nav>
        </div>
      </header>

      <main className="container mx-auto px-6">
        {/* Hero */}
        <section className="py-20 md:py-28 grid lg:grid-cols-2 gap-12 lg:items-end">
          <h1 className="text-4xl md:text-6xl leading-[1.1]">
            <span className="block text-muted-foreground font-light">Read everything once.</span>
            <span className="block font-medium text-foreground">Cite it forever.</span>
          </h1>
          <div className="space-y-6">
            <p className="text-base text-muted-foreground leading-relaxed max-w-md">
              CramBrain turns your PDFs into a study partner that answers questions with the
              exact page and quote behind every claim, then turns the same material into
              quizzes.
            </p>
            <div className="flex flex-wrap items-center gap-3">
              <Link href="/upload">
                <Button size="lg">
                  Upload documents
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <Link href="/chat">
                <Button size="lg" variant="outline">
                  Ask a question
                </Button>
              </Link>
            </div>
          </div>
        </section>

        {/* Dashboard-style preview card */}
        <section className="pb-20">
          <Card>
            <CardContent className="p-8 md:p-10">
              <div className="grid sm:grid-cols-3 gap-10">
                {previewColumns.map(({ icon: Icon, label, title, description }) => (
                  <div key={label}>
                    <div className="flex items-center gap-2 mb-4">
                      <Icon className="h-4 w-4 text-muted-foreground" />
                      <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">
                        {label}
                      </p>
                    </div>
                    <p className="text-lg font-medium mb-1">{title}</p>
                    <p className="text-sm text-muted-foreground">{description}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </section>

        {/* How it Works */}
        <section className="py-16 border-t border-border">
          <h2 className="text-2xl md:text-3xl mb-12">
            <span className="text-muted-foreground">How it</span>{' '}
            <span className="font-medium">works</span>
          </h2>
          <div className="grid md:grid-cols-4 gap-8">
            {steps.map((step) => (
              <div key={step.number} className="border-t border-border pt-6">
                <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground mb-4">
                  {step.number}
                </p>
                <h3 className="font-medium mb-2">{step.title}</h3>
                <p className="text-sm text-muted-foreground">{step.description}</p>
              </div>
            ))}
          </div>
        </section>
      </main>

      {/* Footer / CTA */}
      <footer className="bg-foreground text-background mt-12">
        <div className="container mx-auto px-6 py-16">
          <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-8 mb-16">
            <h2 className="text-3xl md:text-4xl font-medium max-w-md">
              Ready to study smarter?
            </h2>
            <Link href="/upload">
              <Button size="lg" variant="secondary">
                Get started
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>
          <div className="grid sm:grid-cols-3 gap-8 pt-8 border-t border-background/10 text-sm">
            <div className="space-y-2">
              <p className="text-xs uppercase tracking-[0.2em] text-background/50 mb-3">
                Product
              </p>
              <Link href="/upload" className="block text-background/70 hover:text-background">
                Upload
              </Link>
              <Link href="/chat" className="block text-background/70 hover:text-background">
                Chat
              </Link>
              <Link href="/quiz" className="block text-background/70 hover:text-background">
                Quiz
              </Link>
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-background/50 mb-3">
                CramBrain
              </p>
              <p className="text-background/70 max-w-xs">
                An AI study assistant that turns your documents into cited answers and quizzes.
              </p>
            </div>
            <div className="sm:text-right">
              <p className="text-background/50">&copy; 2025 CramBrain.</p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
