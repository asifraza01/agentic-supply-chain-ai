// src/app/action-queue/page.tsx
"use client"
import { ActionQueue } from "@/components/ActionQueue";
import { useState } from "react";

export default function ActionQueuePage() {
  const [actions, setActions] = useState([]) 

  return (
    <div className="flex h-screen flex-col items-stretch justify-start space-y-4 p-4 px-2">
    <ActionQueue actions={actions} setActions={setActions}  />
    </div>
  );
}

/* import { Button } from "@/components/ui/button"
import { Check, X, AlertCircle } from "lucide-react"

const queueData = [
  { id: "Q-94", task: "Approve Deployment Payload", source: "CI/CD Pipeline" },
  { id: "Q-95", task: "Re-index SQLite Search Vectors", source: "Cron Engine" },
  { id: "Q-96", task: "Verify Suspicious Gateway IP", source: "Security Module" },
]

export default function ActionQueuePage() {
  const runAction = (type: string, id: string) => {
    alert(`Dispatched [${type}] action handler sequence target ID: ${id}`)
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold tracking-tight">Action Queue Matrix</h1>
      <div className="rounded-xl border bg-card overflow-hidden shadow-sm">
        <table className="w-full text-left text-sm border-collapse">
          <thead className="bg-muted/50 border-b font-medium text-muted-foreground">
            <tr>
              <th className="p-4 w-24">ID</th><th className="p-4">Assignment Task</th><th className="p-4">Origin Hub</th><th className="p-4 text-right pr-6">Operational Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {queueData.map((row) => (
              <tr key={row.id} className="hover:bg-muted/30">
                <td className="p-4 font-mono text-xs">{row.id}</td>
                <td className="p-4 font-medium">{row.task}</td>
                <td className="p-4 text-muted-foreground">{row.source}</td>
                <td className="p-4 text-right pr-6">
                  <div className="flex justify-end gap-2">
                    <Button size="sm" variant="outline" className="text-emerald-600 hover:text-emerald-700 bg-emerald-50/50 hover:bg-emerald-50" onClick={() => runAction("Accept", row.id)}>
                      <Check className="h-3.5 w-3.5 mr-1" /> Accept
                    </Button>
                    <Button size="sm" variant="outline" className="text-amber-600 hover:text-amber-700 bg-amber-50/50 hover:bg-amber-50" onClick={() => runAction("Escalate", row.id)}>
                      <AlertCircle className="h-3.5 w-3.5 mr-1" /> Escalate
                    </Button>
                    <Button size="sm" variant="outline" className="text-destructive hover:bg-destructive/5" onClick={() => runAction("Reject", row.id)}>
                      <X className="h-3.5 w-3.5 mr-1" /> Reject
                    </Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
 */