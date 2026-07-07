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

import { ReviewModal } from "./ReviewModal"

//import { chatWindow } from "./ChatWindow"


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
  //chat_message:string;
}


 
//export function ActionQueue({ actions, setActions }: { actions: ActionItem[], setActions: any }) 
export function ActionQueue({ actions, setActions }: { actions: ActionItem[], setActions: React.Dispatch<React.SetStateAction<ActionItem[]>> }) {
 
  //const [actions, setActions] = useState<ActionItem[]>([]);
  const [selectedItem, setSelectedItem] = useState<ActionItem | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

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
  }, []);

  const handleApprove = async (thread_id: string) => {
    if (!thread_id) return;
    try {
      await fetch("http://127.0.0.1:8001/api/approve-action", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ thread_id, action: "approve" }),
      });
      setIsModalOpen(false);
    } catch (error) {
      console.error("Failed to approve:", error);
    }
  };

  const handleReject = async (thread_id: string) => {
    if (!thread_id) return;
    try {
      await fetch("http://127.0.0.1:8001/api/approve-action", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ thread_id, action: "reject" }),
      });
      setIsModalOpen(false);
    } catch (error) {
      console.error("Failed to reject:", error);
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
                        className="bg-green-600 hover:bg-green-700 text-white"
                      >
                        Approve
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleReject(item.thread_id)}
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

      <ReviewModal 
      item={selectedItem} 
      isOpen={isModalOpen} 
      onClose={() => setIsModalOpen(false)}
      onApprove={(id) => handleApprove(id)}
      onReject={(id) => handleReject(id)}
      />
    </>
  )
}