This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Project Structure

```
web/
├── src/
│   └── app/
│       ├── api/
│       │   └── chat/
│       │       └── route.ts      # Chat API endpoint (AWS Bedrock)
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

## Environment Setup

Create a `.env.local` file in the `web/` directory (same level as `package.json`):

```bash
# web/.env.local
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-west-2
BEDROCK_MODEL_ID=meta.llama3-8b-instruct-v1:0
```

> **Note**: The app runs in demo mode without AWS credentials — no setup required for basic testing.

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
