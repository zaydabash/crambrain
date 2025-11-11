import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import '../styles/globals.css'
import { ToastProvider } from '@/components/ToastProvider'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'CramBrain - AI Study Assistant',
  description: 'Upload your study materials and get AI-powered answers with citations',
  keywords: ['study', 'AI', 'education', 'PDF', 'quiz', 'learning'],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-background">
          {children}
        </div>
        <ToastProvider />
      </body>
    </html>
  )
}
