# sentio-plus

Idea for project due tuesday:
"Product Review Chat bot"
function: embeds reviews for each product, allows natural language queries

natural language queries for overal customer sentiment. eg "do people like the mac 2025 keyboard?"
response: "people have been saying the keybaord is mid"
natural language query for specific reviews eg "have people been saying bad things about the keyboard?"
response: "here are some reviews epople have said negatively about the keyboard: review1, review2, review3"


S3
ChromaDB
langchain
LLM-Bedrock
Code-local->lam da (preffered)

Evidence-Backed Product Feedback Analysis using RAG

## Overview




## Problem Statement -> What does this solve?
Modern organizations collect massive volumes of customer feedback through product reviews, surveys, and digital channels. While sentiment scores and star ratings provide surface-level signals, they fail to answer the most important business questions:

- Why are customers dissatisfied?

- What issues are driving rating changes?

- Which problems should leadership prioritize fixing first?

This project is designed to function as an internal decision-support tool for Product, CX, and Strategy teams. Rather than simply classifying sentiment, the system **translates unstructured customer feedback into actionable business insights** that inform *product prioritization, roadmap decisions, and customer experience improvements.*

## Key Capabilities

- Scalable ingestion of customer reviews via Amazon S3
- Sentiment analysis to structure raw feedback
- Semantic search using ChromaDB
- RAG pipeline powered by AWS Bedrock LLMs
- Evidence-grounded natural language insights
- Business-ready summaries, root causes, and trends
- Local code execution with cloud-based model services

## Data
We use the *Google Play Store Reviews* dataset (sourced from Kaggle) to power the sentiment analysis and insight generation in this project.

**Dataset:** [Google Play Store Reviews](https://www.kaggle.com/datasets/prakharrathi25/google-play-store-reviews/data)
**Contents:** ~12,000 user review texts with corresponding ratings and metadata for apps
**Use case:** Textual sentiment analysis to infer product strengths, weaknesses, and customer perception trends.




## Pipeline


## Real World Application
### Consulting & Enterprise Use Cases
- Voice of Customer analysis for large platforms
- Product launch and post-release monitoring
- Operational risk detection
- Executive reporting and decision support
- Cost reduction through automation of manual analysis

### Industries
- Technology & consumer electronics
- Healthcare (patient experience feedback)
- Financial services (customer complaints)
- Retail & e-commerce
- SaaS and digital platforms




## Roles
### Carlos & Hayden
- Langchain integration, API, ChromaDB

### Chenchen & Jeffrey
- Documentation, Research Additional Data Sources
- AWS
- Simple Figma mockup ~ Chenchen (optional)

### Kyle & Marlon
- Context Engineering, Prompt Engineering
- Website, UI/UX, API Expected Deliverables