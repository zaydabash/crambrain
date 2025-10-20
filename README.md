# CramBrain Web App

AI-powered study assistant with PDF upload, Q&A, and quiz generation.

## Features

- **PDF Upload**: Drag-and-drop PDF upload with S3 storage
- **AI Q&A**: Ask questions and get answers with citations
- **Quiz Generation**: Generate quizzes from your documents
- **Clickable Citations**: Navigate directly to source pages
- **PDF Viewer**: Interactive PDF viewer with page anchors
- **Study Plans**: Generate 20-minute cram plans
- **Concept Graphs**: Visualize topic connections
- **Spaced Repetition**: Smart study scheduling

## Tech Stack

- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **UI Components**: shadcn/ui
- **PDF Processing**: PDF.js, react-pdf
- **API**: Connects to CramBrain API

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env.local
   ```
   
   Update `.env.local` with your API URL:
   ```
   NEXT_PUBLIC_API_BASE_URL=https://your-api-url.com
   ```

4. Run the development server:
   ```bash
   npm run dev
   ```

5. Open [http://localhost:3000](http://localhost:3000) in your browser

## Deployment

### Vercel (Recommended)

1. Install Vercel CLI:
   ```bash
   npm i -g vercel
   ```

2. Deploy:
   ```bash
   vercel --prod
   ```

### Other Platforms

The app can be deployed to any platform that supports Next.js:
- Netlify
- Railway
- Render
- AWS Amplify

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `NEXT_PUBLIC_API_BASE_URL` | URL of your CramBrain API | Yes |

## Project Structure

```
├── app/                 # Next.js App Router pages
├── components/          # React components
│   ├── ui/             # shadcn/ui components
│   ├── Chat.tsx        # Chat interface
│   ├── FileDrop.tsx    # File upload
│   ├── PdfViewer.tsx   # PDF viewer
│   └── Quiz.tsx        # Quiz interface
├── lib/                # Utility functions
├── styles/             # Global styles
└── public/             # Static assets
```

## API Integration

This web app connects to the CramBrain API for:
- File upload and processing
- AI-powered Q&A
- Quiz generation
- Document management

Make sure your API is running and accessible at the URL specified in `NEXT_PUBLIC_API_BASE_URL`.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details.
