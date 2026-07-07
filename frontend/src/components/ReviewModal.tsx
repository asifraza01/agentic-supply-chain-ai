import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { ScrollArea } from "@/components/ui/scroll-area"

// Interface matching the REAL API response
interface RawActionItem {
  thread_id: string;
  store_id: number;
  sku: string;
  inventory_data: { product_name: string; current_stock: number; reorder_point: number };
  sales_velocity_data: { daily_velocity: number; trend: string };
  contract_context: string;
  reorder_calculation: { recommended_order_quantity: number; reasoning: string };
  proposal: string;
  confidence: number;
}

interface ReviewModalProps {
  item: RawActionItem | null;
  isOpen: boolean;
  onClose: () => void;
  onApprove: (id: string) => void;
  onReject: (id: string) => void;
}

export function ReviewModal({ item, isOpen, onClose, onApprove, onReject }: ReviewModalProps) {
  if (!item) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="!w-[98vw] !max-w-[98vw] h-[90vh] flex flex-col p-0 overflow-hidden">
        {/* Header */}
        <DialogHeader className="px-6 pt-6 pb-4 border-b bg-slate-50">
          <div className="flex items-center justify-between">
            <div>
              <DialogTitle className="text-xl flex items-center gap-3">
                Review Decision: {item.inventory_data?.product_name || "Unknown Product"}
              </DialogTitle>
              <DialogDescription className="text-sm text-slate-500 mt-1">
                Store #{item.store_id} • SKU: {item.sku} • Thread ID: {item.thread_id}
              </DialogDescription>
            </div>
            <Badge variant="outline" className="text-blue-600 border-blue-200 bg-blue-50">
              AI Confidence: {(item.confidence * 100).toFixed(0)}%
            </Badge>
          </div>
        </DialogHeader>

        {/* 3-Column Glass Box Body */}
        <ScrollArea className="flex-1 px-6 py-4">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Column 1: The Deterministic Math */}
            <div className="space-y-4">
              <h3 className="font-semibold text-slate-900 flex items-center gap-2">
                🧮 Optimizer Agent (Math)
              </h3>
              <div className="bg-slate-900 text-slate-100 p-4 rounded-lg font-mono text-sm space-y-2">
                <div className="flex justify-between">
                  <span className="text-slate-400">Current Stock:</span>
                  <span>{item.inventory_data?.current_stock || 0} units</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Daily Velocity:</span>
                  <span>{item.sales_velocity_data?.daily_velocity || 0} units/day</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Trend:</span>
                  <span>{item.sales_velocity_data?.trend || "N/A"}</span>
                </div>
                <Separator className="bg-slate-700 my-2" />
                <div className="flex justify-between text-green-400 font-bold">
                  <span>Calculated Order:</span>
                  <span>{item.reorder_calculation?.recommended_order_quantity || 0} units</span>
                </div>
              </div>
              <p className="text-xs text-slate-500">
                * Calculated using deterministic Python tools. Zero LLM hallucination risk.
              </p>
            </div>

            {/* Column 2: The RAG Context */}
            <div className="space-y-4">
              <h3 className="font-semibold text-slate-900 flex items-center gap-2">
                📑 Investigator Agent (RAG Context)
              </h3>
              <div className="bg-amber-50 border border-amber-200 p-4 rounded-lg space-y-3">
                <p className="text-xs font-bold text-amber-800 uppercase tracking-wide">
                  Retrieved from Qdrant Vector DB
                </p>
                <p className="text-sm text-slate-700 italic leading-relaxed whitespace-pre-line">
                  {item.contract_context || "No specific contract context retrieved."}
                </p>
              </div>
              <p className="text-xs text-slate-500">
                * Unstructured supplier contracts and SLAs parsed via LlamaIndex.
              </p>
            </div>

            {/* Column 3: The AI Proposal */}
            <div className="space-y-4">
              <h3 className="font-semibold text-slate-900 flex items-center gap-2">
                💬 Explainer Agent (Proposal)
              </h3>
              <div className="bg-white border border-slate-200 p-4 rounded-lg shadow-sm">
                <p className="text-sm text-slate-800 leading-relaxed whitespace-pre-line">
                  {item.proposal || "Waiting for proposal generation..."}
                </p>
              </div>
            </div>

          </div>
        </ScrollArea>

        {/* Footer Actions */}
        <DialogFooter className="px-6 py-4 border-t bg-slate-50 flex justify-end gap-3">
          <Button variant="outline" onClick={() => onReject(item.thread_id)} className="text-red-600 hover:text-red-700 hover:bg-red-50 border-red-200">
            Reject
          </Button>
          <Button onClick={() => onApprove(item.thread_id)} className="bg-green-600 hover:bg-green-700 text-white">
            Approve & Execute PO
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}