"use client"

import { useState, useEffect } from "react"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Textarea } from "@/components/ui/textarea"

import { ReviewModal } from "./ReviewModal"

export interface ActionItem {
  thread_id: string;
  store_id: number;
  sku: string;
  inventory_data: { product_name: string; current_stock: number };
  sales_velocity_data: { daily_velocity: number };
  reorder_calculation: { recommended_order_quantity: number };
  proposal: string;
  contract_context: string;
  confidence: number;
}

export function ActionQueue({ 
  actions, 
  setActions 
}: { 
  actions: ActionItem[], 
  setActions: React.Dispatch<React.SetStateAction<ActionItem[]>> 
}) {
  const [selectedItem, setSelectedItem] = useState<ActionItem | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  // ✅ NEW: States for rejection flow
  const [isRejectModalOpen, setIsRejectModalOpen] = useState(false);
  const [rejectionReason, setRejectionReason] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [itemToReject, setItemToReject] = useState<ActionItem | null>(null);

  // 🚨 POLLING: Use 127.0.0.1 to prevent Ubuntu IPv6 NetworkErrors
  useEffect(() => {
    const fetchActions = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8001/api/pending-actions");
        if (response.ok) {
          const data = await response.json();
          setActions(data);
        }
      } catch (error) {
        console.error("Failed to fetch actions:", error);
      }
    };

    fetchActions(); 
    const interval = setInterval(fetchActions, 3000); 
    return () => clearInterval(interval);
  }, [setActions]); // Added setActions to dependency array for safety

  const handleApprove = async (thread_id: string) => {
    if (!thread_id) return;
    setIsProcessing(true);
    try {
      const response = await fetch("http://127.0.0.1:8001/api/approve-action", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ thread_id, action: "approve" }),
      });
      
      if (response.ok) {
        // ✅ Optimistically update UI: remove the approved item instantly
        setActions(prev => prev.filter(item => item.thread_id !== thread_id));
        setIsModalOpen(false);
      }
    } catch (error) {
      console.error("Failed to approve:", error);
    } finally {
      setIsProcessing(false);
    }
  };

  // ✅ NEW: Open the rejection dialog instead of immediately rejecting
  const openRejectDialog = (thread_id: string) => {
    const item = actions.find(a => a.thread_id === thread_id) || selectedItem;
    if (item) {
      setItemToReject(item);
      setRejectionReason("");
      setIsModalOpen(false); // Close review modal if it's currently open
      setIsRejectModalOpen(true);
    }
  };

  // ✅ NEW: Confirm rejection with reason
  const confirmReject = async () => {
    if (!itemToReject) return;
    setIsProcessing(true);
    try {
      const response = await fetch("http://127.0.0.1:8001/api/approve-action", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          thread_id: itemToReject.thread_id, 
          action: "reject",
          reason: rejectionReason.trim() || "No reason provided" // ✅ Send the reason to backend
        }),
      });
      
      if (response.ok) {
        // ✅ Optimistically update UI: remove the rejected item instantly
        setActions(prev => prev.filter(item => item.thread_id !== itemToReject.thread_id));
        setIsRejectModalOpen(false);
        setItemToReject(null);
        setRejectionReason("");
      } else {
        console.error("Failed to reject:", await response.text());
      }
    } catch (error) {
      console.error("Failed to reject:", error);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <>
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Action Queue (Human-in-the-Loop)</CardTitle>
            <Badge variant="secondary">{actions.length} Pending</Badge>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Store</TableHead>
                <TableHead>Product</TableHead>
                <TableHead>Proposed Action</TableHead>
                <TableHead>Confidence</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {actions.map((item) => (
                <TableRow key={item.thread_id || `action-${item.store_id}-${item.sku}`}>
                  <TableCell className="font-medium">#{item.store_id}</TableCell>
                  <TableCell>
                    <div className="flex flex-col">
                      <span className="font-medium">{item.inventory_data?.product_name || "Unknown"}</span>
                      <span className="text-xs text-slate-500">{item.sku}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    Reorder {item.reorder_calculation?.recommended_order_quantity || 0} units
                  </TableCell>
                  <TableCell>{((item.confidence || 0) * 100).toFixed(0)}%</TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-2">
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => { setSelectedItem(item); setIsModalOpen(true); }}
                      >
                        Review
                      </Button>
                      <Button 
                        size="sm"
                        onClick={() => handleApprove(item.thread_id)}
                        disabled={isProcessing}
                        className="bg-green-600 hover:bg-green-700 text-white"
                      >
                        {isProcessing ? "..." : "Approve"}
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => openRejectDialog(item.thread_id)}
                        disabled={isProcessing}
                        className="text-red-600 hover:text-red-700 hover:bg-red-50 border-red-200"
                      >
                        Reject
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
              {actions.length === 0 && (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-8 text-slate-500">
                    🎉 All caught up! No pending approvals.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Review Modal (3-column Glass Box) */}
      <ReviewModal 
        item={selectedItem} 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)}
        onApprove={(id) => handleApprove(id)}
        onReject={(id) => openRejectDialog(id)} // ✅ Redirects to the new rejection dialog
      />

      {/* ✅ NEW: Rejection Reason Dialog */}
      <Dialog open={isRejectModalOpen} onOpenChange={setIsRejectModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Reject Purchase Order</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <p className="text-sm text-muted-foreground">
              Please provide a reason for rejecting this recommendation. This will be saved in the audit trail.
            </p>
            <Textarea
              placeholder="e.g., Overstock concern, budget constraints, wrong supplier, seasonal item..."
              value={rejectionReason}
              onChange={(e) => setRejectionReason(e.target.value)}
              rows={4}
            />
          </div>
          <DialogFooter>
            <Button 
              variant="outline" 
              onClick={() => {
                setIsRejectModalOpen(false);
                setItemToReject(null);
                setRejectionReason("");
              }}
              disabled={isProcessing}
            >
              Cancel
            </Button>
            <Button 
              variant="destructive" 
              onClick={confirmReject}
              disabled={isProcessing}
            >
              {isProcessing ? "Processing..." : "Confirm Rejection"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}