/* // src/app/chat/page.tsx
"use client"

import {ChatWindow} from "@/components/ChatWindow"; // Adjust path as needed
import {ChatInterface} from "@/components/ThreadId"
import { useState } from "react";

export default function ChatPage() {
const [threadId, setThreadId] = useState<string | null>(null);

  return (
    <div className="flex h-screen w-full items-stretch justify-start space-y-4 p-4 px-2">
    <ChatInterface threadId={threadId} setThreadId={setThreadId} /> 
    
    
    </div>
  );
} */


"use client";

import React, { useState } from "react";
import ThreadSessionSelector from "@/components/ThreadSessionSelector";
import ChatConsoleBox from "@/components/ChatConsoleBox";

export default function OrderChatPage() {
  // Tracks and maps a fixed permanent ID per user across the two child nodes
  const [currentThreadId, setCurrentThreadId] = useState<string>("user_exec_main_session");

  return (
    <main className="p-6 md:p-10 max-w-7xl mx-auto bg-slate-50/40 min-h-screen space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">AI Control Command Portal</h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Interactive chat session connected to LangGraph execution checkpointers
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 items-start">
        {/* Left Side: Session controls layer column */}
        <div className="lg:col-span-1">
          <ThreadSessionSelector threadId={currentThreadId} setThreadId={setCurrentThreadId} />
        </div>

        {/* Right Side: Primary conversational log area card */}
        <div className="lg:col-span-3">
          <ChatConsoleBox threadId={currentThreadId} />
        </div>
      </div>
    </main>
  );
}
