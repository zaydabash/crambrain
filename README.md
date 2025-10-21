# CramBrain

**Transform your study materials into an intelligent learning companion**

CramBrain revolutionizes how students interact with their study materials. Upload your PDFs, ask questions, and get instant answers with precise page citations. Generate custom quizzes and master your content through intelligent spaced repetition.

## Why CramBrain?

**Stop wasting time searching through documents.** CramBrain understands your content and delivers exactly what you need, when you need it.

- **Instant Answers**: Ask questions in natural language and get responses with exact page references
- **Smart Citations**: Click any citation to jump directly to the relevant page in your document
- **Adaptive Quizzes**: Generate personalized quizzes that adapt to your learning pace
- **Study Plans**: Get structured 20-minute cram sessions tailored to your material
- **Concept Mapping**: Visualize how topics connect across your documents
- **Spaced Repetition**: Optimize your study schedule for maximum retention

## Key Features

### Intelligent Document Processing
Upload PDFs and watch CramBrain extract, analyze, and index your content with precision. Our advanced processing handles text, images, tables, and complex layouts.

### Conversational Learning
Ask questions exactly as you would to a tutor. "Explain the difference between mitosis and meiosis" or "What are the key points from chapter 3?" Get comprehensive answers with source citations.

### Interactive PDF Viewer
Navigate your documents seamlessly with our integrated PDF viewer. Citations become clickable links that take you directly to the relevant content.

### Adaptive Quiz Generation
Generate quizzes that match your study needs:
- Multiple choice questions
- Short answer prompts  
- Fill-in-the-blank exercises
- Custom difficulty levels

### Study Optimization
- **Cram Plans**: Get structured 20-minute study sessions
- **Concept Graphs**: See how topics interconnect
- **Spaced Repetition**: Optimize review timing for long-term retention

## Technology Stack

**Frontend Architecture**
- Next.js 14 with App Router for optimal performance
- TypeScript for type safety and developer experience
- Tailwind CSS for responsive, modern design
- shadcn/ui components for consistent user interface

**Document Processing**
- PDF.js for client-side PDF rendering
- react-pdf for seamless PDF integration
- Advanced text extraction and chunking algorithms

**API Integration**
- RESTful API communication
- Real-time file upload with progress tracking
- Optimistic UI updates for smooth user experience

## Quick Start

### Prerequisites
- Node.js 18 or higher
- npm or yarn package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/crambrain-web.git
   cd crambrain-web
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env.local
   ```
   
   Update `.env.local` with your API endpoint:
   ```env
   NEXT_PUBLIC_API_BASE_URL=https://your-crambrain-api.com
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

5. **Open your browser**
   Navigate to [http://localhost:3000](http://localhost:3000)

## Deployment

### Vercel (Recommended)
Deploy to Vercel with zero configuration:

```bash
npm install -g vercel
vercel --prod
```

### Alternative Platforms
CramBrain works on any platform supporting Next.js:
- **Netlify**: Static site generation with edge functions
- **Railway**: Full-stack deployment with database support  
- **Render**: Containerized deployment with auto-scaling
- **AWS Amplify**: Enterprise-grade hosting with CDN

## Configuration

| Variable | Description | Required |
|----------|-------------|----------|
| `NEXT_PUBLIC_API_BASE_URL` | CramBrain API endpoint URL | Yes |

## Project Architecture

```
├── app/                    # Next.js App Router
│   ├── (marketing)/       # Landing page routes
│   ├── chat/              # Q&A interface
│   ├── upload/            # Document upload
│   ├── quiz/              # Quiz generation
│   └── docs/[docId]/      # Document viewer
├── components/            # Reusable React components
│   ├── ui/               # Design system components
│   ├── Chat.tsx          # Conversational interface
│   ├── FileDrop.tsx      # Drag-and-drop upload
│   ├── PdfViewer.tsx     # Interactive PDF viewer
│   └── Quiz.tsx          # Quiz interface
├── lib/                  # Utility functions and API client
├── styles/               # Global styles and themes
└── public/               # Static assets
```

## API Integration

CramBrain connects to a powerful backend API that handles:

- **Document Processing**: Advanced PDF parsing and content extraction
- **Vector Search**: Semantic search across your documents
- **Question Answering**: Natural language processing for accurate responses
- **Quiz Generation**: Intelligent question creation based on content analysis
- **Study Analytics**: Progress tracking and optimization recommendations

Ensure your CramBrain API is running and accessible at the configured endpoint.

## About

CramBrain was created to solve a fundamental problem in education: students spend too much time searching for information instead of learning. By combining advanced document processing with intelligent question answering, CramBrain transforms static study materials into interactive learning experiences.

The platform is designed for students who want to study smarter, not harder. Whether you're preparing for exams, researching topics, or reviewing course materials, CramBrain adapts to your learning style and helps you retain information more effectively.

## Release Notes

### Version 1.0.0
**Initial Release**

- Complete document upload and processing pipeline
- Intelligent question answering with page citations
- Interactive PDF viewer with clickable references
- Quiz generation with multiple question types
- Study plan creation and spaced repetition
- Concept graph visualization
- Responsive design for all devices
- Real-time upload progress and status updates

## Contributing

We welcome contributions from developers who share our vision of making learning more efficient and engaging.

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

Please ensure your code follows our style guidelines and includes appropriate tests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Support

For questions, bug reports, or feature requests, please open an issue on GitHub or contact our support team.

---

**Ready to revolutionize your study routine?** [Get started with CramBrain today](https://your-crambrain-url.com)