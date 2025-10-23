import { z } from 'zod'

// API Base URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://cram-brain-api-v1.onrender.com'

// Schemas
export const PresignRequestSchema = z.object({
  filename: z.string(),
})

export const PresignResponseSchema = z.object({
  upload_url: z.string(),
  file_url: z.string(),
  file_id: z.string(),
})

export const IngestRequestSchema = z.object({
  file_url: z.string(),
  original_name: z.string(),
})

export const IngestResponseSchema = z.object({
  doc_id: z.string(),
  pages: z.number(),
  chunks: z.number(),
  status: z.string(),
})

export const QueryRequestSchema = z.object({
  query: z.string(),
  top_k: z.number().min(1).max(20).default(6),
  doc_id: z.string().optional(),
})

export const CitationSchema = z.object({
  doc_id: z.string(),
  page: z.number(),
  bbox_id: z.string().optional(),
  preview_url: z.string(),
  source_url: z.string(),
  quote: z.string(),
})

export const RetrievalResultSchema = z.object({
  doc_id: z.string(),
  page: z.number(),
  bbox_id: z.string().optional(),
  text: z.string(),
  score: z.number(),
  preview_url: z.string(),
  source_url: z.string(),
})

export const QueryResponseSchema = z.object({
  answer: z.string(),
  citations: z.array(CitationSchema),
  retrieval: z.array(RetrievalResultSchema),
})

export const QuizQuestionSchema = z.object({
  type: z.enum(['short_answer', 'multiple_choice', 'cloze']),
  prompt: z.string(),
  options: z.array(z.string()).optional(),
  answer: z.string(),
  page: z.number(),
  quote: z.string(),
})

export const QuizRequestSchema = z.object({
  doc_id: z.string().optional(),
  topic: z.string().optional(),
  n: z.number().min(1).max(20).default(10),
})

export const QuizResponseSchema = z.object({
  questions: z.array(QuizQuestionSchema),
  doc_id: z.string().optional(),
})

export const DocumentMetadataSchema = z.object({
  doc_id: z.string(),
  original_name: z.string(),
  file_url: z.string(),
  preview_urls: z.array(z.string()),
  pages: z.number(),
  chunks: z.number(),
  created_at: z.string(),
  updated_at: z.string(),
})

export const DocumentListResponseSchema = z.object({
  documents: z.array(DocumentMetadataSchema),
})

export const SearchResponseSchema = z.object({
  query: z.string(),
  results: z.array(RetrievalResultSchema),
  total: z.number(),
})

// Types
export type PresignRequest = z.infer<typeof PresignRequestSchema>
export type PresignResponse = z.infer<typeof PresignResponseSchema>
export type IngestRequest = z.infer<typeof IngestRequestSchema>
export type IngestResponse = z.infer<typeof IngestResponseSchema>
export type QueryRequest = z.infer<typeof QueryRequestSchema>
export type QueryResponse = z.infer<typeof QueryResponseSchema>
export type Citation = z.infer<typeof CitationSchema>
export type RetrievalResult = z.infer<typeof RetrievalResultSchema>
export type QuizQuestion = z.infer<typeof QuizQuestionSchema>
export type QuizRequest = z.infer<typeof QuizRequestSchema>
export type QuizResponse = z.infer<typeof QuizResponseSchema>
export type DocumentMetadata = z.infer<typeof DocumentMetadataSchema>
export type DocumentListResponse = z.infer<typeof DocumentListResponseSchema>
export type SearchResponse = z.infer<typeof SearchResponseSchema>

// API Client
class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    })

    if (!response.ok) {
      const error = await response.text()
      throw new Error(`API Error: ${response.status} ${error}`)
    }

    return response.json()
  }

  // Health check
  async healthCheck() {
    return this.request<{ status: string; time: string }>('/v1/health')
  }

  // Presign upload
  async presignUpload(filename: string): Promise<PresignResponse> {
    const response = await this.request<PresignResponse>('/v1/presign', {
      method: 'POST',
      body: JSON.stringify({ filename }),
    })
    return PresignResponseSchema.parse(response)
  }

  // Ingest document
  async ingestDocument(fileUrl: string, originalName: string): Promise<IngestResponse> {
    const response = await this.request<IngestResponse>('/v1/ingest', {
      method: 'POST',
      body: JSON.stringify({ file_url: fileUrl, original_name: originalName }),
    })
    return IngestResponseSchema.parse(response)
  }

  // Ask question
  async askQuestion(query: string, docId?: string, topK: number = 6): Promise<QueryResponse> {
    const response = await this.request<QueryResponse>('/v1/ask', {
      method: 'POST',
      body: JSON.stringify({ query, doc_id: docId, top_k: topK }),
    })
    return QueryResponseSchema.parse(response)
  }

  // Generate quiz
  async generateQuiz(docId?: string, topic?: string, n: number = 10): Promise<QuizResponse> {
    const response = await this.request<QuizResponse>('/v1/quiz', {
      method: 'POST',
      body: JSON.stringify({ doc_id: docId, topic, n }),
    })
    return QuizResponseSchema.parse(response)
  }

  // List documents
  async listDocuments(): Promise<DocumentListResponse> {
    const response = await this.request<DocumentListResponse>('/v1/docs')
    return DocumentListResponseSchema.parse(response)
  }

  // Get document
  async getDocument(docId: string): Promise<DocumentMetadata> {
    const response = await this.request<DocumentMetadata>(`/v1/docs/${docId}`)
    return DocumentMetadataSchema.parse(response)
  }

  // Search documents
  async searchDocuments(query: string, docId?: string, limit: number = 10): Promise<SearchResponse> {
    const params = new URLSearchParams({ q: query, limit: limit.toString() })
    if (docId) params.append('doc_id', docId)
    
    const response = await this.request<SearchResponse>(`/v1/search?${params}`)
    return SearchResponseSchema.parse(response)
  }
}

// Export singleton instance
export const apiClient = new ApiClient()
export default apiClient
