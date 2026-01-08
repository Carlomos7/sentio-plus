"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Image from "next/image";
import Link from "next/link";
import {
  ArrowLeft,
  Send,
  Sparkles,
  Trash2,
  MessageSquare,
  Loader2,
} from "lucide-react";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: number;
}

interface ChatSession {
  id: string;
  title: string;
  messages: Message[];
  createdAt: number;
}

const STORAGE_KEY = "sentio-chat-sessions";
const SAMPLE_QUESTIONS = [
  "What are the main complaints about our mobile app?",
  "What do customers love most about our product?",
  "Show me sentiment trends from last month",
  "Which features get the most negative feedback?",
];

export default function DemoPage() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const activeSession = sessions.find((s) => s.id === activeSessionId);
  const messages = activeSession?.messages || [];

  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      const parsed = JSON.parse(stored);
      setSessions(parsed);
      if (parsed.length > 0) {
        setActiveSessionId(parsed[0].id);
      }
    }
  }, []);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions));
  }, [sessions]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const createNewSession = () => {
    const newSession: ChatSession = {
      id: crypto.randomUUID(),
      title: "New Chat",
      messages: [],
      createdAt: Date.now(),
    };
    setSessions((prev) => [newSession, ...prev]);
    setActiveSessionId(newSession.id);
  };

  const deleteSession = (id: string) => {
    setSessions((prev) => prev.filter((s) => s.id !== id));
    if (activeSessionId === id) {
      const remaining = sessions.filter((s) => s.id !== id);
      setActiveSessionId(remaining.length > 0 ? remaining[0].id : null);
    }
  };

  const sendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return;

    let sessionId = activeSessionId;
    if (!sessionId) {
      const newSession: ChatSession = {
        id: crypto.randomUUID(),
        title: content.slice(0, 30) + (content.length > 30 ? "..." : ""),
        messages: [],
        createdAt: Date.now(),
      };
      setSessions((prev) => [newSession, ...prev]);
      sessionId = newSession.id;
      setActiveSessionId(sessionId);
    }

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: content.trim(),
      timestamp: Date.now(),
    };

    setSessions((prev) =>
      prev.map((s) => {
        if (s.id === sessionId) {
          const updatedMessages = [...s.messages, userMessage];
          return {
            ...s,
            messages: updatedMessages,
            title:
              s.messages.length === 0
                ? content.slice(0, 30) + (content.length > 30 ? "..." : "")
                : s.title,
          };
        }
        return s;
      })
    );

    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: content,
          sessionId,
        }),
      });

      const data = await response.json();

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: data.response || "I encountered an error processing your request.",
        timestamp: Date.now(),
      };

      setSessions((prev) =>
        prev.map((s) =>
          s.id === sessionId
            ? { ...s, messages: [...s.messages, assistantMessage] }
            : s
        )
      );
    } catch {
      const errorMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: "Sorry, I encountered an error. Please try again.",
        timestamp: Date.now(),
      };

      setSessions((prev) =>
        prev.map((s) =>
          s.id === sessionId
            ? { ...s, messages: [...s.messages, errorMessage] }
            : s
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

  return (
    <div className="min-h-screen bg-sentio-light flex">
      {/* Sidebar */}
      <aside className="w-72 bg-white border-r border-sentio-border flex flex-col">
        <div className="p-4 border-b border-sentio-border">
          <Link href="/" className="flex items-center gap-2 mb-4">
            <Image
              src="/sentio-logo.png"
              alt="Sentio"
              width={100}
              height={28}
              className="h-7 w-auto"
            />
          </Link>
          <button
            onClick={createNewSession}
            className="w-full px-4 py-3 rounded-xl btn-primary text-white font-medium flex items-center justify-center gap-2"
          >
            <Sparkles className="w-4 h-4" />
            New Chat
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-3 space-y-1">
          {sessions.map((session) => (
            <motion.div
              key={session.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className={`group relative flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer transition-colors ${
                activeSessionId === session.id
                  ? "bg-sentio-blue/10 text-sentio-blue"
                  : "hover:bg-sentio-light text-sentio-gray"
              }`}
              onClick={() => setActiveSessionId(session.id)}
            >
              <MessageSquare className="w-4 h-4 flex-shrink-0" />
              <span className="text-sm truncate flex-1">{session.title}</span>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  deleteSession(session.id);
                }}
                className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-100 rounded transition-all"
              >
                <Trash2 className="w-3.5 h-3.5 text-red-500" />
              </button>
            </motion.div>
          ))}

          {sessions.length === 0 && (
            <div className="text-center py-8 text-sentio-gray text-sm">
              No conversations yet.
              <br />
              Start a new chat!
            </div>
          )}
        </div>

        <div className="p-4 border-t border-sentio-border">
          <Link
            href="/"
            className="flex items-center gap-2 text-sm text-sentio-gray hover:text-sentio-dark transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Home
          </Link>
        </div>
      </aside>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col">
        {/* Header */}
        <header className="h-16 bg-white border-b border-sentio-border flex items-center px-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-sentio-blue to-sentio-blue-light flex items-center justify-center">
              <MessageSquare className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="font-semibold text-sentio-dark">Sentio AI</h1>
              <p className="text-xs text-sentio-gray">
                Context from all 12,495 reviews
              </p>
            </div>
          </div>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center max-w-lg"
              >
                <div className="w-16 h-16 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-sentio-blue to-sentio-blue-light flex items-center justify-center p-3">
                  <Image
                    src="/snetio-logo(white).png"
                    alt="Sentio"
                    width={80}
                    height={80}
                    className="w-full h-full object-contain"
                  />
                </div>
                <h2 className="text-2xl font-bold text-sentio-dark mb-2">
                  Welcome to Sentio Demo
                </h2>
                <p className="text-sentio-gray mb-8">
                  Ask me anything about your customer reviews. I can analyze
                  sentiment, find patterns, and surface insights.
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {SAMPLE_QUESTIONS.map((question, i) => (
                    <motion.button
                      key={i}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.1 }}
                      onClick={() => sendMessage(question)}
                      className="p-4 text-left text-sm rounded-xl border border-sentio-border bg-white hover:bg-sentio-light hover:border-sentio-blue/30 transition-all text-sentio-gray hover:text-sentio-dark"
                    >
                      {question}
                    </motion.button>
                  ))}
                </div>
              </motion.div>
            </div>
          ) : (
            <div className="max-w-3xl mx-auto space-y-4">
              <AnimatePresence mode="popLayout">
                {messages.map((msg) => (
                  <motion.div
                    key={msg.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0 }}
                    className={`flex ${
                      msg.role === "user" ? "justify-end" : "justify-start"
                    }`}
                  >
                    <div
                      className={`max-w-[85%] rounded-2xl px-5 py-3 ${
                        msg.role === "user"
                          ? "bg-gradient-to-r from-sentio-blue to-sentio-blue-light text-white"
                          : "bg-white border border-sentio-border text-sentio-dark card-shadow"
                      }`}
                    >
                      <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>

              {isLoading && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex justify-start"
                >
                  <div className="bg-white border border-sentio-border rounded-2xl px-5 py-3 card-shadow">
                    <div className="flex items-center gap-2 text-sentio-gray">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span className="text-sm">Analyzing...</span>
                    </div>
                  </div>
                </motion.div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-sentio-border bg-white">
          <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
            <div className="flex items-center gap-3 p-2 rounded-2xl bg-sentio-light border border-sentio-border focus-within:border-sentio-blue/50 focus-within:ring-2 focus-within:ring-sentio-blue/10 transition-all">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about your reviews..."
                className="flex-1 bg-transparent px-3 py-2 outline-none text-sentio-dark placeholder:text-sentio-gray"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={!input.trim() || isLoading}
                className="w-10 h-10 rounded-xl bg-gradient-to-r from-sentio-blue to-sentio-blue-light flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed transition-opacity"
              >
                <Send className="w-5 h-5 text-white" />
              </button>
            </div>
            <p className="text-xs text-sentio-gray text-center mt-2">
              Demo mode — responses are simulated. Connect to AWS Bedrock for
              real AI analysis.
            </p>
          </form>
        </div>
      </main>
    </div>
  );
}
