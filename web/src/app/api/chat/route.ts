import { NextRequest, NextResponse } from "next/server";
import { BedrockRuntimeClient, InvokeModelCommand } from "@aws-sdk/client-bedrock-runtime";

const AWS_REGION = process.env.AWS_REGION || "us-west-2";
const BEDROCK_MODEL_ID = process.env.BEDROCK_MODEL_ID || "meta.llama3-8b-instruct-v1:0";
const isDemoMode = !process.env.AWS_ACCESS_KEY_ID || 
                   !process.env.AWS_SECRET_ACCESS_KEY || 
                   process.env.AWS_ACCESS_KEY_ID === "your_access_key_here";

const DEMO_RESPONSES: Record<string, string> = {
  complaints: `Based on 2,341 reviews mentioning the mobile app, the top 3 concerns are:

**Slow loading times** (38% of complaints) - Users report the app taking 5-10 seconds to load on first launch. Most affected: Android users on older devices.

**Checkout bugs** (27%) - Intermittent payment failures and cart clearing issues, especially during peak hours.

**Push notification issues** (19%) - Users report either receiving no notifications or getting duplicate alerts.

I can dive deeper into any of these areas if you'd like.`,

  positive: `Based on 8,234 positive reviews, customers consistently praise three key areas:

**Ease of use** (mentioned in 72% of positive reviews) - Customers frequently use words like "intuitive", "simple", and "just works". Key highlights include one-click setup (412 mentions) and clean interface (387 mentions).

**Customer support responsiveness** (64%) - Average response time praised is under 2 hours. Live chat rated 4.8/5.

**Value for money** (58%) - Particularly strong sentiment among small business users who compare favorably against enterprise alternatives.`,

  sentiment: `Sentiment trends over the last 30 days show:

**Overall Sentiment**: 67% positive (+3% from previous month)
**Neutral**: 21% (-1%)  
**Negative**: 12% (-2%)

**Notable shifts**:
- Mobile app sentiment improved 8% after the v2.3.1 patch
- Customer service mentions became 15% more positive following new chat feature
- Pricing sentiment stable despite recent adjustments

**Emerging topics**: "dark mode" requests up 340%, "API access" mentions growing steadily.`,

  negative: `Features receiving the most negative feedback (last 90 days):

**1. Mobile App Performance** (847 negative mentions)
Primary issues: Load times, crashes on Android, battery drain

**2. Reporting Dashboard** (423 mentions)  
Users find it "confusing" and "too complex". Export functionality frequently criticized.

**3. Notification System** (312 mentions)
Email notifications often delayed or land in spam. Push notifications unreliable.

**4. Billing Portal** (289 mentions)
Invoice download issues, unclear subscription management.

Would you like specific quotes or deeper analysis on any of these?`,
};

function getDemoResponse(message: string): string {
  const lower = message.toLowerCase();

  if (lower.includes("complaint") || lower.includes("problem") || lower.includes("issue") || lower.includes("mobile")) {
    return DEMO_RESPONSES.complaints;
  }
  if (lower.includes("love") || lower.includes("positive") || lower.includes("like") || lower.includes("praise")) {
    return DEMO_RESPONSES.positive;
  }
  if (lower.includes("sentiment") || lower.includes("trend") || lower.includes("month")) {
    return DEMO_RESPONSES.sentiment;
  }
  if (lower.includes("negative") || lower.includes("worst") || lower.includes("bad") || lower.includes("feature")) {
    return DEMO_RESPONSES.negative;
  }

  return `I've analyzed your query across 12,847 customer reviews. Here's what I found:

Based on the semantic search, your question relates to customer feedback patterns we've identified. The data shows a mix of sentiment with actionable insights available.

**Key Finding**: Customer feedback consistently highlights areas for product improvement while also acknowledging strengths.

Try asking more specific questions like:
- "What are the main complaints about our mobile app?"
- "What do customers love most about our product?"
- "Show me sentiment trends from last month"

I'm here to help you understand your customers better!`;
}

async function getBedrockResponse(message: string): Promise<string> {
  const client = new BedrockRuntimeClient({
    region: AWS_REGION,
    credentials: {
      accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
      secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
    },
  });

  const systemPrompt = `You are Sentio AI, a customer review analysis assistant. You help users understand patterns in customer feedback using semantic search and AI analysis. You are analyzing a database of 12,495 customer reviews. Be concise and data-driven. Use specific numbers and percentages. Highlight actionable insights.`;

  const body = JSON.stringify({
    prompt: `<s>[INST] <<SYS>>\n${systemPrompt}\n<</SYS>>\n\n${message} [/INST]`,
    max_gen_len: 1000,
    temperature: 0.1,
  });

  const command = new InvokeModelCommand({
    modelId: BEDROCK_MODEL_ID,
    contentType: "application/json",
    accept: "application/json",
    body: body,
  });

  const response = await client.send(command);
  const responseBody = JSON.parse(new TextDecoder().decode(response.body));
  
  let rawResponse = responseBody.generation || responseBody.content || "Unable to generate response.";
  
  const stopSequences = ['</s>', '<</SYS>>', '[/INST]', '<<SYS>>[/INST]'];
  for (const stop of stopSequences) {
    const index = rawResponse.indexOf(stop);
    if (index !== -1) {
      rawResponse = rawResponse.substring(0, index);
    }
  }
  
  const tokensToRemove = [
    '<<SYS>>[/INST]',
    '<</SYS>>',
    '[INST]',
    '[/INST]',
    '<<SYS>>',
    '</SYS>',
    '<SYS>',
  ];
  
  for (const token of tokensToRemove) {
    while (rawResponse.includes(token)) {
      rawResponse = rawResponse.split(token).join('');
    }
  }
  
  if (rawResponse.includes(systemPrompt)) {
    const promptIndex = rawResponse.indexOf(systemPrompt);
    rawResponse = rawResponse.substring(0, promptIndex).trim();
  }
  
  return rawResponse.trim();
}

export async function POST(request: NextRequest) {
  try {
    const { message } = await request.json();

    if (!message || typeof message !== "string") {
      return NextResponse.json({ error: "Message is required" }, { status: 400 });
    }

    let response: string;

    if (isDemoMode) {
      await new Promise((resolve) => setTimeout(resolve, 800 + Math.random() * 700));
      response = getDemoResponse(message);
    } else {
      response = await getBedrockResponse(message);
    }

    return NextResponse.json({ response });
  } catch (error) {
    console.error("Chat API error:", error);
    return NextResponse.json(
      { error: "Failed to process request", response: getDemoResponse("fallback") },
      { status: 500 }
    );
  }
}