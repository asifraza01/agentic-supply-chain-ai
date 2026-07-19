"use client";

import React from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Database, Plus, RefreshCw } from "lucide-react";

interface SelectorProps {
  threadId: string;
  setThreadId: (id: string) => void;
}

export default function ThreadSessionSelector({ threadId, setThreadId }: SelectorProps) {
  // Generates a clean production-ready unique string format identifier
  const generateNewUUIDThread = () => {
    const randomId = Math.random().toString(36).substring(2, 11);
    setThreadId(`user_exec_thread_${randomId}`);
  };

  return (
    <Card className="w-full bg-white border border-slate-100 shadow-sm">
      <CardHeader className="pb-4">
        <CardTitle className="text-sm font-semibold flex items-center gap-2 text-slate-800">
          <Database className="h-4 w-4 text-blue-600" />
          Session Persistence Controls
        </CardTitle>
        <CardDescription className="text-xs">
          Mapped to permanent SQLite checkpoint storage tables
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-1.5">
          <label htmlFor="thread-input" className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
            Active Thread Identity:
          </label>
          <input
            id="thread-input"
            type="text"
            value={threadId}
            onChange={(e) => setThreadId(e.target.value)}
            className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-xs font-mono font-bold text-slate-700 shadow-inner focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all"
            placeholder="Enter tracking token..."
          />
        </div>

        <div className="flex gap-2">
          <button
            onClick={generateNewUUIDThread}
            className="flex-1 inline-flex items-center justify-center gap-1.5 bg-slate-100 hover:bg-slate-200 active:bg-slate-300 text-slate-700 font-semibold text-xs py-2 px-3 rounded-lg border border-slate-200 shadow-sm transition-all focus:outline-none focus:ring-2 focus:ring-slate-400"
          >
            <Plus className="h-3.5 w-3.5" />
            New Session
          </button>
        </div>

        <div className="pt-2 border-t border-slate-50 flex items-center gap-2 text-[10px] font-medium text-slate-400">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          Synced securely with local cache indices
        </div>
      </CardContent>
    </Card>
  );
}
