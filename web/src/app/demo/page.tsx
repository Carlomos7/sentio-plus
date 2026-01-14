"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Image from "next/image";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import {
  ArrowLeft,
  Send,
  Sparkles,
  Trash2,
  MessageSquare,
  Loader2,
  Pencil,
  Check,
} from "lucide-react";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: number;
  sources?: string[];
  numDocs?: number;
}

interface ChatSession {
  id: string;
  title: string;
  messages: Message[];
  createdAt: number;
}

const STORAGE_KEY = "sentio-chat-sessions";
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const SAMPLE_QUESTIONS = [
  "What are the trends for negative reviews in finance apps?",
  "Which health & fitness apps have the best user retention feedback?",
  "Compare sentiment patterns between food delivery apps",
  "What features drive 5-star reviews in productivity apps?",
];

export default function DemoPage() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [editingSessionId, setEditingSessionId] = useState<string | null>(null);
  const [editingTitle, setEditingTitle] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const editInputRef = useRef<HTMLInputElement>(null);
  const headerInputRef = useRef<HTMLInputElement>(null);

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

  const startEditing = (session: ChatSession) => {
    setEditingSessionId(session.id);
    setEditingTitle(session.title);
    setTimeout(() => editInputRef.current?.focus(), 0);
  };

  const saveTitle = () => {
    if (editingSessionId && editingTitle.trim()) {
      setSessions((prev) =>
        prev.map((s) =>
          s.id === editingSessionId ? { ...s, title: editingTitle.trim() } : s
        )
      );
    }
    setEditingSessionId(null);
    setEditingTitle("");
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
      const response = await fetch(`${API_URL}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: content.trim(),
          filter_by_source: true,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `API error: ${response.status}`);
      }

      const data = await response.json();

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: data.answer || "I couldn't generate a response.",
        timestamp: Date.now(),
        sources: data.sources || [],
        numDocs: data.num_docs || 0,
      };

      setSessions((prev) =>
        prev.map((s) =>
          s.id === sessionId
            ? { ...s, messages: [...s.messages, assistantMessage] }
            : s
        )
      );
    } catch (error) {
      const errorMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content:
          error instanceof Error
            ? `Sorry, I encountered an error: ${error.message}. Please make sure the FastAPI backend is running.`
            : "Sorry, I encountered an error. Please try again.",
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
            <span className="text-lg font-semibold text-sentio-dark">Sentio</span>
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
              {editingSessionId === session.id ? (
                <input
                  ref={editInputRef}
                  type="text"
                  value={editingTitle}
                  onChange={(e) => setEditingTitle(e.target.value)}
                  onBlur={saveTitle}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") saveTitle();
                    if (e.key === "Escape") {
                      setEditingSessionId(null);
                      setEditingTitle("");
                    }
                  }}
                  onClick={(e) => e.stopPropagation()}
                  className="text-sm flex-1 bg-white border border-sentio-blue rounded px-2 py-0.5 outline-none"
                />
              ) : (
                <span className="text-sm truncate flex-1">{session.title}</span>
              )}
              <div className="flex items-center gap-1">
                {editingSessionId === session.id ? (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      saveTitle();
                    }}
                    className="p-1 hover:bg-sentio-blue/20 rounded transition-all"
                  >
                    <Check className="w-3.5 h-3.5 text-sentio-blue" />
                  </button>
                ) : (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      startEditing(session);
                    }}
                    className="opacity-0 group-hover:opacity-100 p-1 hover:bg-sentio-blue/20 rounded transition-all"
                  >
                    <Pencil className="w-3.5 h-3.5 text-sentio-blue" />
                  </button>
                )}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteSession(session.id);
                  }}
                  className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-100 rounded transition-all"
                >
                  <Trash2 className="w-3.5 h-3.5 text-red-500" />
                </button>
              </div>
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
              {editingSessionId === activeSessionId && activeSession ? (
                <input
                  ref={headerInputRef}
                  type="text"
                  value={editingTitle}
                  onChange={(e) => setEditingTitle(e.target.value)}
                  onBlur={saveTitle}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") saveTitle();
                    if (e.key === "Escape") {
                      setEditingSessionId(null);
                      setEditingTitle("");
                    }
                  }}
                  className="font-semibold text-sentio-dark bg-sentio-light border border-sentio-blue rounded px-2 py-0.5 outline-none"
                />
              ) : (
                <h1
                  className="font-semibold text-sentio-dark cursor-pointer hover:text-sentio-blue transition-colors"
                  onClick={() => {
                    if (activeSession) {
                      setEditingSessionId(activeSession.id);
                      setEditingTitle(activeSession.title);
                      setTimeout(() => headerInputRef.current?.focus(), 0);
                    }
                  }}
                >
                  {activeSession?.title || "Sentio AI"}
                </h1>
              )}
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
                      {msg.role === "assistant" ? (
                        <div className="text-sm markdown-content">
                          <ReactMarkdown
                            components={{
                              p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                              h1: ({ children }) => <h1 className="text-lg font-bold mb-2 mt-3 first:mt-0">{children}</h1>,
                              h2: ({ children }) => <h2 className="text-base font-bold mb-2 mt-3 first:mt-0">{children}</h2>,
                              h3: ({ children }) => <h3 className="text-sm font-semibold mb-2 mt-3 first:mt-0">{children}</h3>,
                              ul: ({ children }) => <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>,
                              ol: ({ children }) => <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>,
                              li: ({ children }) => <li className="ml-2">{children}</li>,
                              code: ({ children, className }) => {
                                const isInline = !className;
                                return isInline ? (
                                  <code className="bg-sentio-light text-sentio-blue px-1.5 py-0.5 rounded text-xs font-mono">
                                    {children}
                                  </code>
                                ) : (
                                  <code className={className}>{children}</code>
                                );
                              },
                              pre: ({ children }) => (
                                <pre className="bg-sentio-light border border-sentio-border rounded-lg p-3 overflow-x-auto mb-2 text-xs">
                                  {children}
                                </pre>
                              ),
                              strong: ({ children }) => <strong className="font-semibold text-sentio-dark">{children}</strong>,
                              em: ({ children }) => <em className="italic">{children}</em>,
                              a: ({ href, children }) => (
                                <a
                                  href={href}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-sentio-blue underline hover:text-sentio-blue-light"
                                >
                                  {children}
                                </a>
                              ),
                              blockquote: ({ children }) => (
                                <blockquote className="border-l-4 border-sentio-blue pl-4 italic text-sentio-gray my-2">
                                  {children}
                                </blockquote>
                              ),
                              hr: () => <hr className="my-3 border-sentio-border" />,
                            }}
                          >
                            {msg.content}
                          </ReactMarkdown>
                        </div>
                      ) : (
                        <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                      )}
                      {msg.role === "assistant" && msg.sources && msg.sources.length > 0 && (
                        <div className="mt-3 pt-3 border-t border-sentio-border">
                          <p className="text-xs text-sentio-gray mb-2">
                            Sources ({msg.numDocs || msg.sources.length} documents):
                          </p>
                          <div className="flex flex-wrap gap-2">
                            {msg.sources.map((source, idx) => (
                              <span
                                key={idx}
                                className="px-2 py-1 text-xs rounded-full bg-sentio-blue/10 text-sentio-blue border border-sentio-blue/20"
                              >
                                {source}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
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
              Powered by FastAPI RAG backend • Using semantic search and AI analysis
            </p>
          </form>
        </div>
      </main>
    </div>
  );
}
