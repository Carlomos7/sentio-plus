This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Project Structure

```
web/
├── src/
│   └── app/
│       ├── demo/
│       │   └── page.tsx          # Demo chat interface
│       ├── globals.css           # Global styles & Tailwind
│       ├── layout.tsx            # Root layout
│       └── page.tsx              # Landing page
├── public/                       # Static assets (logos, icons)
├── .env.local                    # Environment variables (create this)
├── package.json
├── tailwind.config.ts
└── tsconfig.json
```

## Architecture

The web frontend communicates with the FastAPI backend (`app/`) which provides:
- **RAG (Retrieval-Augmented Generation)** queries via `/query` endpoint
- Vector search through ChromaDB
- LLM integration with AWS Bedrock

**Flow:** Web Frontend → FastAPI `/query` → RAG Service → Vector Store + AWS Bedrock

## Environment Setup

Create a `.env.local` file in the `web/` directory (same level as `package.json`):

```bash
# web/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

> **Note**: Make sure the FastAPI backend is running before using the demo. The backend handles all AWS credentials and LLM configuration.

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Prerequisites

Before running the web frontend, ensure the FastAPI backend is running:

1. Navigate to the `app/` directory
2. Start the FastAPI server (typically on port 8000)
3. The web frontend will connect to the backend automatically

See the `app/README.md` for FastAPI setup instructions.
