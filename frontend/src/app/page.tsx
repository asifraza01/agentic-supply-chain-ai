import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-50 p-8">
      {/* Header */}
      <header className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">
            Supply Chain Control Tower
          </h1>
          <p className="text-slate-500">
            Agentic AI Orchestrator with Human-in-the-Loop Governance
          </p>
        </div>
        <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200 font-medium px-3 py-1">
          🟢 System Operational
        </Badge>
      </header>

      {/* Metric Cards */}
      <div className="grid gap-4 md:grid-cols-3 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Approvals</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">3</div>
            <p className="text-xs text-slate-500">+2 since last hour</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Stockouts Prevented</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">12</div>
            <p className="text-xs text-slate-500">Last 30 days</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Auto-Drafted POs</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">48</div>
            <p className="text-xs text-slate-500">Total value: $124,500</p>
          </CardContent>
        </Card>
      </div>

      {/* Action Queue Placeholder */}
      <Card>
        <CardHeader>
          <CardTitle>Action Queue (Human-in-the-Loop)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-32 border-2 border-dashed rounded-lg bg-slate-50">
            <p className="text-slate-500">Action Queue Component Loading Next...</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}