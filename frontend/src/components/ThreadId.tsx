"use client"

import {ChatWindow} from "@/components/ChatWindow"
import { useState, useEffect, use } from 'react';
// import { PostgresSaver } from "@langchain/langgraph-checkpoint-postgres"; // Server-side

// Helper to safely access localStorage only in the browser
const getPersistentThreadId = () => {
  if (typeof window === 'undefined') return null;
  
  let threadId = localStorage.getItem('langgraph_thread_id');
  if (!threadId) {
    threadId = crypto.randomUUID();
    localStorage.setItem('langgraph_thread_id', threadId);
  }
  return threadId;
};

export function ChatInterface() {
  const [threadId, setThreadId] = useState<string | null>(null);

  // Initialize threadId after component mounts (client-side)
  useEffect(() => {
    setThreadId(getPersistentThreadId());
  }, []);

  if (!threadId) return <div>Loading session...</div>;

  return (
    <ChatWindow threadId={threadId} />  // ← Pass as prop
  );
}
