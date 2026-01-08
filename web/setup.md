# Sentio Plus - Setup Guide

## Prerequisites

- Node.js v18+ (recommended: v20+)
- npm or yarn

## Installation

```bash
cd web
npm install
```

## Environment Variables (Optional)

For full AI functionality with AWS Bedrock, create a `.env.local` file:

```bash
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-west-2
BEDROCK_MODEL_ID=meta.llama3-8b-instruct-v1:0
```

> **Note**: The app runs in demo mode without AWS credentials - no setup required for basic testing.

## Running the App

```bash
# Development server
npm run dev

# Production build
npm run build
npm run start
```

The app runs at `http://localhost:3000`

## Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Create production build |
| `npm run start` | Run production server |
| `npm run lint` | Run ESLint |
