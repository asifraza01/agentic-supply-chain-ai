// src/app/page.tsx

import { redirect } from "next/navigation"
import PurchaseOrdersPage  from "@/components/Dashboard";

export default function RootEntryPage() {
  // Automatically bounces root traffic into your Dashboard layout node safely
  //redirect("/PurchaseOrdersPage")
   return (
      <div className="flex h-screen flex-col items-stretch justify-start space-y-4 p-4 px-2">
      <PurchaseOrdersPage  />
      </div>
    );
}