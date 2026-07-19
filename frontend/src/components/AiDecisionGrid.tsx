"use client";

import React, { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Bot, Loader2, CheckCircle2, AlertCircle, HelpCircle, ShieldCheck } from "lucide-react";

interface DecisionItem {
  id: number;
  timestamp: string;
  poNumber: string;
  storeId: number;
  sku: string;
  productName: string;
  quantity: number;
  status: string;
  reasoning: string;
}

export default function AiDecisionGrid() {
  const [history, setHistory] = useState<DecisionItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [processingId, setProcessingId] = useState<string | null>(null);

  const fetchLogs = () => {
    fetch("http://localhost:8001/api/dashboard/ai-history")
      .then((res) => res.json())
      .then((data) => {
        setHistory(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  // Action 1: Post Safety Threshold modifications dynamically
  const handleSliderChange = async (storeId: number, sku: string, value: number) => {
    try {
      await fetch("http://localhost:8001/api/inventory/update-threshold", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ store_id: storeId, sku, new_threshold: value }),
      });
      fetchLogs(); // Hot-reloads charts and layouts nearby
    } catch (err) {
      console.error("Threshold modification failed:", err);
    }
  };

  // Action 2: Promote Draft loops to Autonomous active statuses
  const handlePromoteOrder = async (poNumber: string) => {
    setProcessingId(poNumber);
    try {
      await fetch("http://localhost:8001/api/purchase-orders/promote", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ po_number: poNumber, user_name: "Manager Override" }),
      });
      fetchLogs();
    } catch (err) {
      console.error("Order promotion failed:", err);
    } finally {
      setProcessingId(null);
    }
  };

  if (loading) {
    return (
      <div className="flex p-8 items-center justify-center gap-2 border rounded-xl bg-white shadow-sm">
        <Loader2 className="h-5 w-5 animate-spin text-purple-600" />
        <span className="text-sm text-slate-500 font-medium">Syncing agentic audit trails...</span>
      </div>
    );
  }

  return (
    <Card className="w-full border border-slate-100 shadow-sm bg-white">
      <CardHeader className="flex flex-row items-center gap-3 space-y-0">
        <div className="p-2 bg-purple-50 text-purple-600 rounded-lg">
          <Bot className="h-5 w-5" />
        </div>
        <div>
          <CardTitle className="text-base font-semibold">LangGraph Automation Log & Decision Engine</CardTitle>
          <CardDescription className="text-xs">Human-In-The-Loop (HITL) panel to adjust agent parameters or overwrite pipeline drafts</CardDescription>
        </div>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto border border-slate-100 rounded-xl">
          <table className="min-w-full divide-y divide-slate-100 text-left text-sm">
            <thead className="bg-slate-50/70 text-slate-500 text-xs font-semibold uppercase tracking-wider">
              <tr>
                <th className="p-4">Target SKU Node</th>
                <th className="p-4">Agent Actions</th>
                <th className="p-4">Tweak Safety Limit</th>
                <th className="p-4 text-center">Pipeline Routing</th>
                <th className="p-4 text-center">HITL Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-600">
              {history.length === 0 ? (
                <tr>
                  <td colSpan={5} className="p-8 text-center text-slate-400 font-medium">No autonomous LangGraph events logged.</td>
                </tr>
              ) : (
                history.map((row) => (
                  <tr key={row.id} className="hover:bg-slate-50/40 transition-colors">
                    <td className="p-4">
                      <div className="font-semibold text-slate-800">{row.sku}</div>
                      <div className="text-xs text-slate-400 truncate">{row.productName} (Store #{row.storeId})</div>
                    </td>
                    <td className="p-4">
                      <div className="font-medium text-slate-700">Generated {row.poNumber}</div>
                      <div className="text-xs text-slate-400 font-mono">{row.quantity} units · {row.timestamp}</div>
                    </td>
                    {/* Interactive Slider Input Column */}
                    <td className="p-4 max-w-[180px]">
                      <div className="flex flex-col gap-1">
                        <input 
                          type="range" 
                          min="10" 
                          max="100" 
                          defaultValue="25"
                          onMouseUp={(e) => handleSliderChange(row.storeId, row.sku, parseInt(e.currentTarget.value))}
                          onTouchEnd={(e) => handleSliderChange(row.storeId, row.sku, parseInt(e.currentTarget.value))}
                          className="w-full h-1.5 bg-slate-100 rounded-lg appearance-none cursor-pointer accent-blue-600"
                        />
                        <span className="text-[10px] text-slate-400 font-medium font-mono text-center">Release to sync safety bound</span>
                      </div>
                    </td>
                    <td className="p-4 text-center whitespace-nowrap">
                      {row.status.toUpperCase() === "APPROVED" ? (
                        <span className="inline-flex items-center gap-1 bg-green-50 text-green-700 px-2.5 py-0.5 rounded-full text-xs font-semibold border border-green-200"><CheckCircle2 className="h-3 w-3" /> Autonomous</span>
                      ) : (
                        <span className="inline-flex items-center gap-1 bg-amber-50 text-amber-700 px-2.5 py-0.5 rounded-full text-xs font-semibold border border-amber-200"><HelpCircle className="h-3 w-3" /> Human-In-Loop</span>
                      )}
                    </td>
                    {/* Action Execution Button Column */}
                    <td className="p-4 text-center whitespace-nowrap">
                      {row.status.toUpperCase() === "DRAFT" ? (
                        <button
                          onClick={() => handlePromoteOrder(row.poNumber)}
                          disabled={processingId === row.poNumber}
                          className="inline-flex items-center gap-1 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-semibold text-xs px-3 py-1.5 rounded-lg shadow-sm transition-all focus:outline-none focus:ring-2 focus:ring-blue-400"
                        >
                          {processingId === row.poNumber ? (
                            <Loader2 className="h-3 w-3 animate-spin" />
                          ) : (
                            <ShieldCheck className="h-3.5 w-3.5" />
                          )}
                          Approve Draft
                        </button>
                      ) : (
                        <span className="text-xs text-slate-400 font-medium italic">Execution Locked</span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}
