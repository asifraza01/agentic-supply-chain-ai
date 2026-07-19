"use client";

import React, { useState, useRef, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Bot, Send, User, Loader2, Sparkles } from "lucide-react";

interface Message {
  sender: "user" | "ai";
  text: string;
  timestamp: string;
}

interface ChatProps {
  threadId: string;
}

export default function ChatConsoleBox({ threadId }: ChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scrolls conversation container down to display the latest updates
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  // Handle payload execution over local network boundaries
  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userText = input.trim();
    setInput("");
    setLoading(true);

    const timeString = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    // Optimistically update the UI timeline with user text entry
    setMessages((prev) => [...prev, { sender: "user", text: userText, timestamp: timeString }]);

    try {
      const response = await fetch("http://localhost:8001/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ thread_id: threadId, message: userText }),
      });

      if (!response.ok) throw new Error("API worker returned an invalid operational status.");
      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        { sender: "ai", text: data.reply, timestamp: timeString },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { sender: "ai", text: "Communication Failure: Unable to sync with the internal LangGraph engine.", timestamp: timeString },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="w-full border border-slate-100 shadow-sm bg-white flex flex-col h-[550px]">
      <CardHeader className="flex flex-row items-center gap-3 space-y-0 border-b border-slate-50 pb-4">
        <div className="p-2 bg-purple-50 text-purple-600 rounded-lg shadow-sm">
          <Bot className="h-5 w-5" />
        </div>
        <div>
          <CardTitle className="text-base font-semibold flex items-center gap-1.5 text-slate-800">
            Supply Chain Audit Assistant
            <Sparkles className="h-3.5 w-3.5 text-amber-500 fill-amber-50" />
          </CardTitle>
          <CardDescription className="text-xs">
            Query Inventory logs, decision context layers, or supplier SLA contracts
          </CardDescription>
        </div>
      </CardHeader>

      {/* Main Conversation Container Viewport */}
      <CardContent className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50/50">
        {messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-center p-6 space-y-2">
            <Bot className="h-10 w-10 text-slate-300 stroke-[1.5]" />
            <p className="text-sm font-semibold text-slate-700">Analytical Workspace Active</p>
            <p className="text-xs text-slate-400 max-w-[280px]">Try asking: "Show me stock levels for SKU-APP-101 at Store 101" or "Why did you create order PO-LNGRPH-8420?"</p>
          </div>
        )}

        {messages.map((msg, index) => (
          <div key={index} className={`flex gap-3 ${msg.sender === "user" ? "justify-end" : "justify-start"}`}>
            {msg.sender === "ai" && (
              <div className="w-7 h-7 rounded-full bg-purple-50 border border-purple-100 text-purple-600 flex items-center justify-center flex-shrink-0 text-xs shadow-sm"><Bot className="h-4 w-4" /></div>
            )}
            <div className="flex flex-col space-y-1 max-w-[80%]">
              <div className={`p-3 rounded-2xl text-sm leading-relaxed shadow-sm font-medium ${
                msg.sender === "user"
                  ? "bg-blue-600 text-white rounded-tr-none"
                  : "bg-white text-slate-700 border border-slate-100 rounded-tl-none"
              }`}>
                {msg.text}
              </div>
              <span className={`text-[10px] text-slate-400 font-semibold px-1 ${msg.sender === "user" ? "text-right" : "text-left"}`}>
                {msg.timestamp}
              </span>
            </div>
            {msg.sender === "user" && (
              <div className="w-7 h-7 rounded-full bg-blue-50 border border-blue-100 text-blue-600 flex items-center justify-center flex-shrink-0 text-xs shadow-sm"><User className="h-4 w-4" /></div>
            )}
          </div>
        ))}

        {/* Loading indicator token stream mock */}
        {loading && (
          <div className="flex gap-3 justify-start items-center">
            <div className="w-7 h-7 rounded-full bg-purple-50 border border-purple-100 text-purple-600 flex items-center justify-center animate-spin text-xs"><Loader2 className="h-4 w-4" /></div>
            <div className="bg-white border border-slate-100 text-slate-400 font-semibold text-xs px-4 py-2.5 rounded-2xl rounded-tl-none shadow-sm animate-pulse">
              Agent is analyzing SQLite schemas & checking vector segments...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </CardContent>

      {/* Input Message Form Footer */}
      <form onSubmit={handleSendMessage} className="p-3 border-t border-slate-50 bg-white flex gap-2 items-center">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
          placeholder="Ask anything about the supply chain network..."
          className="flex-1 bg-slate-50 border border-slate-200 rounded-xl py-2.5 px-4 text-sm text-slate-700 placeholder-slate-400 shadow-inner focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="p-2.5 bg-blue-600 hover:bg-blue-700 active:bg-blue-800 disabled:bg-slate-100 text-white disabled:text-slate-300 rounded-xl shadow-sm transition-all focus:outline-none focus:ring-2 focus:ring-blue-400 flex-shrink-0"
        >
          <Send className="h-4 w-4" />
        </button>
      </form>
    </Card>
  );
}
