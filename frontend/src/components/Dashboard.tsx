"use client";

// import React, { useEffect, useState } from "react";
// // import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
// import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
// import { 
//   BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
//   LineChart, Line, PieChart, Pie, Cell, Legend 
// } from "recharts";
// //import { TrendingUp, Bot, Truck, AlertTriangle, Layers, Loader2 } from "lucide-react";
// import { TrendingUp, Bot, Truck, AlertTriangle, Layers, Package, Loader2 } from "lucide-react";


import React, { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  LineChart, Line, PieChart, Pie, Cell, Legend 
} from "recharts";
import { TrendingUp, Bot, Truck, AlertTriangle, Layers, Package, Loader2 } from "lucide-react";
import AiDecisionGrid from "@/components/AiDecisionGrid";


interface ExecutiveData {
  kpis: { totalSold: number; aiApproved: number; inTransit: number };
  salesTrend: { date: string; sales: number }[];
  storePerformance: { store: string; units: number }[];
}

interface RetailData {
  kpis: { stockouts: number; uniqueSkus: number; draftPos: number };
  stockByStore: { store: string; current: number; reorder: number }[];
  poStatus: { name: string; value: number; color: string }[];
}

interface WarehouseData {
  kpis: { needsReorder: number; pendingFulfillment: number; zones: number };
  runway: { name: string; stock: number; min: number }[];
  zoneSpread: { name: string; value: number }[];
}

const PALETTE = ["#3b82f6", "#10b981", "#8b5cf6", "#f59e0b", "#ec4899", "#14b8a6"];


export default function PurchaseOrdersPage() {
  const [currentView, setCurrentView] = useState<"executive" | "retail" | "warehouse">("executive");
  const [execData, setExecData] = useState<ExecutiveData | null>(null);
  const [retailData, setRetailData] = useState<RetailData | null>(null);
  const [warehouseData, setWarehouseData] = useState<WarehouseData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Re-fetch when switching tabs
  useEffect(() => {
    setLoading(true);
    // const endpoint = currentView === "executive" ? "executive" : "retail";
    
    fetch(`http://localhost:8001/api/dashboard/${currentView}`)
      .then((res) => {
        if (!res.ok) throw new Error(`Failed to load ${currentView} metrics.`);
        return res.json();
      })
      .then((fetchedData) => {
        if (currentView === "executive") setExecData(fetchedData);
        else if (currentView === "retail") setRetailData(fetchedData);
        else setWarehouseData(fetchedData);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [currentView]);

  if (loading) {
    return (
      <div className="flex h-screen w-full flex-col items-center justify-center gap-2">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        <p className="text-sm font-medium text-slate-500">Syncing database view...</p>
      </div>
    );
  }

  if (error) {
    return <div className="p-8 text-center text-red-500 font-medium">Error: {error}</div>;
  }

  return (
    <div className="w-full space-y-6 p-6">
      {/* Header Panel with Dropdown Switcher */}
      <div className="pb-4 border-b flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Agentic Supply Chain Hub</h1>
          <p className="text-xs text-muted-foreground">LangGraph Live Operational Profiles</p>
        </div>
        
        {/* Dynamic View Dropdown Menu */}
        <div className="flex items-center gap-2">
          <label htmlFor="view-select" className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Role View:</label>
          <select 
            id="view-select"
            value={currentView}
            onChange={(e) => setCurrentView(e.target.value as "executive" | "retail")}
            className="bg-white border border-slate-200 rounded-lg p-2 text-sm font-medium text-slate-700 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="executive">Supply Chain Executive</option>
            <option value="retail">Retail Business Owner</option>
            <option value="warehouse">Warehouse Floor Manager</option>
          </select>
        </div>
      </div>

      {/* ========================================== */}
      {/* VIEW: EXECUTIVE DASHBOARD */}
      {/* ========================================== */}
      {currentView === "executive" && execData && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardContent className="flex items-center justify-between p-6">
                <div>
                  <p className="text-xs font-medium text-muted-foreground uppercase">Volume Sold</p>
                  <h3 className="text-2xl font-bold mt-1">{execData.kpis.totalSold.toLocaleString()} units</h3>
                </div>
                <div className="p-3 bg-blue-50 text-blue-600 rounded-lg"><TrendingUp className="h-5 w-5" /></div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="flex items-center justify-between p-6">
                <div>
                  <p className="text-xs font-medium text-muted-foreground uppercase">Agent Actions</p>
                  <h3 className="text-2xl font-bold mt-1">{execData.kpis.aiApproved} Autonomous POs</h3>
                </div>
                <div className="p-3 bg-purple-50 text-purple-600 rounded-lg"><Bot className="h-5 w-5" /></div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="flex items-center justify-between p-6">
                <div>
                  <p className="text-xs font-medium text-muted-foreground uppercase">Pipeline Load</p>
                  <h3 className="text-2xl font-bold mt-1">{execData.kpis.inTransit.toLocaleString()} units</h3>
                </div>
                <div className="p-3 bg-green-50 text-green-600 rounded-lg"><Truck className="h-5 w-5" /></div>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card className="lg:col-span-2">
              <CardHeader><CardTitle className="text-base">System-Wide Sales Run Rate</CardTitle></CardHeader>
              <CardContent className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={execData.salesTrend}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="date" fontSize={12} stroke="#94a3b8" />
                    <YAxis fontSize={12} stroke="#94a3b8" />
                    <Tooltip />
                    <Line type="monotone" dataKey="sales" stroke="#3b82f6" strokeWidth={2} dot={{ r: 4 }} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card className="lg:col-span-1">
              <CardHeader><CardTitle className="text-base">Sales Allocation by Store Node</CardTitle></CardHeader>
              <CardContent className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={execData.storePerformance} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis type="number" fontSize={12} stroke="#94a3b8" />
                    <YAxis dataKey="store" type="category" fontSize={11} width={80} stroke="#94a3b8" />
                    <Tooltip />
                    <Bar dataKey="units" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {/* ========================================== */}
      {/* VIEW: RETAIL BUSINESS OWNER */}
      {/* ========================================== */}
      {currentView === "retail" && retailData && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card className="border-red-200 bg-red-50/20">
              <CardContent className="flex items-center justify-between p-6">
                <div>
                  <p className="text-xs font-medium text-red-700 uppercase">Stockouts Present</p>
                  <h3 className="text-2xl font-bold mt-1 text-red-600">{retailData.kpis.stockouts} SKUs</h3>
                </div>
                <div className="p-3 bg-red-100 text-red-600 rounded-lg"><AlertTriangle className="h-5 w-5" /></div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="flex items-center justify-between p-6">
                <div>
                  <p className="text-xs font-medium text-muted-foreground uppercase">Unique SKUs Online</p>
                  <h3 className="text-2xl font-bold mt-1">{retailData.kpis.uniqueSkus} Products</h3>
                </div>
                <div className="p-3 bg-slate-100 text-slate-600 rounded-lg"><Layers className="h-5 w-5" /></div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="flex items-center justify-between p-6">
                <div>
                  <p className="text-xs font-medium text-muted-foreground uppercase">Awaiting Sign-off</p>
                  <h3 className="text-2xl font-bold mt-1">{retailData.kpis.draftPos} Draft POs</h3>
                </div>
                <div className="p-3 bg-amber-50 text-amber-600 rounded-lg"><Bot className="h-5 w-5" /></div>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card className="lg:col-span-2">
              <CardHeader><CardTitle className="text-base">Current Stock vs Reorder Points</CardTitle></CardHeader>
              <CardContent className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={retailData.stockByStore}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="store" fontSize={12} stroke="#94a3b8" />
                    <YAxis fontSize={12} stroke="#94a3b8" />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="current" name="Current Stock" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="reorder" name="Reorder Point" fill="#ef4444" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
               </Card> {/* <--- Added missing closing Card tag here */}

            {/* PO Life-Cycle Donut Card */}
            <Card className="lg:col-span-1">
              <CardHeader>
                <CardTitle className="text-base">PO Life-Cycle Distribution</CardTitle>
              </CardHeader>
              <CardContent className="h-[300px] flex flex-col justify-center items-center">
                <div className="w-full h-[220px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie 
                        data={retailData.poStatus} 
                        dataKey="value" 
                        nameKey="name" 
                        cx="50%" 
                        cy="50%" 
                        innerRadius={60} 
                        outerRadius={80} 
                        paddingAngle={4}
                      >
                        {retailData.poStatus.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="flex flex-wrap gap-4 text-xs font-semibold justify-center">
                  {retailData.poStatus.map((status, i) => (
                    <div key={i} className="flex items-center gap-1.5">
                      <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: status.color }} />
                      <span className="text-slate-600">{status.name} ({status.value})</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}
       {/* ========================================================================= */}
      {/* VIEW 3: WAREHOUSE MANAGER */}
      {/* ========================================================================= */}
      {currentView === "warehouse" && warehouseData && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card className="border-amber-200 bg-amber-50/20">
              <CardContent className="flex items-center justify-between p-6">
                <div>
                  <p className="text-xs font-medium text-amber-700 uppercase">Below Reorder Alert</p>
                  <h3 className="text-2xl font-bold mt-1 text-amber-600">{warehouseData.kpis.needsReorder} Lines</h3>
                </div>
                <div className="p-3 bg-amber-100 text-amber-600 rounded-lg"><AlertTriangle className="h-5 w-5" /></div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="flex items-center justify-between p-6">
                <div>
                  <p className="text-xs font-medium text-muted-foreground uppercase">Fulfillment Backlog</p>
                  <h3 className="text-2xl font-bold mt-1">{warehouseData.kpis.pendingFulfillment} Approved POs</h3>
                </div>
                <div className="p-3 bg-blue-50 text-blue-600 rounded-lg"><Package className="h-5 w-5" /></div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="flex items-center justify-between p-6">
                <div>
                  <p className="text-xs font-medium text-muted-foreground uppercase">Active Layout Footprint</p>
                  <h3 className="text-2xl font-bold mt-1">{warehouseData.kpis.zones} Floor Areas</h3>
                </div>
                <div className="p-3 bg-emerald-50 text-emerald-600 rounded-lg"><Layers className="h-5 w-5" /></div>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle className="text-base">Critical Replenishment Runway Deficits</CardTitle>
                <CardDescription className="text-xs">SKUs currently operating furthest below your database thresholds</CardDescription>
              </CardHeader>
              <CardContent className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={warehouseData.runway}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="name" fontSize={11} stroke="#94a3b8" />
                    <YAxis fontSize={12} stroke="#94a3b8" />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="stock" name="Actual Stock" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="min" name="Minimum Allowed" fill="#e2e8f0" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card className="lg:col-span-1">
              <CardHeader><CardTitle className="text-base">Physical Stock Volume Spread</CardTitle></CardHeader>
              <CardContent className="h-[300px] flex flex-col justify-center items-center">
                <div className="w-full h-[220px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie 
                        data={warehouseData.zoneSpread} 
                        dataKey="value" 
                        nameKey="name" 
                        cx="50%" 
                        cy="50%" 
                        outerRadius={75}
                      >
                        {(warehouseData.zoneSpread || []).map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={PALETTE[index % PALETTE.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="flex flex-wrap gap-3 text-xs font-semibold justify-center">
                  {(warehouseData.zoneSpread || []).map((zone, i) => (
                    <div key={i} className="flex items-center gap-1">
                      <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: PALETTE[i % PALETTE.length] }} />
                      <span className="text-slate-600">{zone.name}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}
      {/* 2. Add the component right here, outside the view blocks, so it shows below everything */}
      <div className="pt-2">
        <AiDecisionGrid />
      </div>

    </div>
  );
}