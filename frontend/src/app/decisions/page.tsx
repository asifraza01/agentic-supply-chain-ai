"use client"

import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import ReactMarkdown from 'react-markdown'

export default function DecisionsPage() {
  const [decisions, setDecisions] = useState([])
  const [selectedDecision, setSelectedDecision] = useState(null)

  useEffect(() => {
    fetch('http://127.0.0.1:8001/api/decisions')
      .then(res => res.json())
      .then(data => setDecisions(data))
  }, [])

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Decision History</h1>
      
      <div className="space-y-4">
        {decisions.map((decision) => (
          <Card key={decision.id}>
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle>{decision.po_number}</CardTitle>
                  <p className="text-sm text-muted-foreground">
                    SKU: {decision.sku} | Store: {decision.store_id} | Qty: {decision.quantity}
                  </p>
                </div>
                <Badge variant={decision.decision === 'APPROVED' ? 'default' : 'destructive'}>
                  {decision.decision}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex justify-between items-center">
                <div>
                  <p className="text-sm">
                    Confidence: {(decision.confidence_score * 100).toFixed(1)}%
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {new Date(decision.decided_at).toLocaleString('de-DE')}
                  </p>
                </div>
                <Button 
                  variant="outline" 
                  onClick={() => setSelectedDecision(decision)}
                >
                  View Details
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Detail Dialog */}
      <Dialog open={!!selectedDecision} onOpenChange={() => setSelectedDecision(null)}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Decision Details: {selectedDecision?.po_number}</DialogTitle>
          </DialogHeader>
          
          {selectedDecision && (
            <div className="space-y-6">
              {/* Basic Info */}
              <div>
                <h3 className="font-semibold mb-2">Basic Information</h3>
                <p>SKU: {selectedDecision.sku}</p>
                <p>Store: {selectedDecision.store_id}</p>
                <p>Quantity: {selectedDecision.quantity}</p>
                <p>Decision: {selectedDecision.decision}</p>
                {selectedDecision.rejection_reason && (
                  <p className="text-red-600">
                    Reason: {selectedDecision.rejection_reason}
                  </p>
                )}
              </div>

              {/* Investigator Context */}
              <div>
                <h3 className="font-semibold mb-2">🔍 Investigator Agent (RAG Context)</h3>
                <div className="bg-muted p-4 rounded-lg">
                  <ReactMarkdown>{selectedDecision.investigator_context}</ReactMarkdown>
                </div>
              </div>

              {/* Optimizer Calculation */}
              <div>
                <h3 className="font-semibold mb-2">🧮 Optimizer Agent (Math)</h3>
                <div className="bg-muted p-4 rounded-lg">
                  <pre className="text-sm overflow-x-auto">
                    {JSON.stringify(JSON.parse(selectedDecision.optimizer_calculation), null, 2)}
                  </pre>
                </div>
              </div>

              {/* Explainer Proposal */}
              <div>
                <h3 className="font-semibold mb-2">💡 Explainer Agent (Proposal)</h3>
                <div className="bg-muted p-4 rounded-lg">
                  <ReactMarkdown>{selectedDecision.explainer_proposal}</ReactMarkdown>
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}