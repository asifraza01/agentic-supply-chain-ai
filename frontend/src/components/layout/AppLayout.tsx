// component/layout/AppLayout.tsx
import * as React from "react"
import { SidebarProvider } from "@/components/ui/sidebar"
import { TooltipProvider } from "@/components/ui/tooltip" // 1. Import the TooltipProvider
import { Sidenavbar } from "../Sidenavbar"
import { Header } from "../Header"
import { Footer } from "../Footer"

export function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <SidebarProvider>
      {/* 2. Wrap everything inside TooltipProvider */}
      <TooltipProvider delayDuration={0}> 
        <div className="flex h-screen w-screen overflow-hidden bg-background">
          
          {/* Leftbar Panel */}
          <Sidenavbar />

          {/* Right Application Window Container */}
          <div className="flex flex-1 flex-col overflow-hidden">
            
            {/* Header Component */}
            <Header />

            {/* Core Content Shell */}
            <main className="flex-1 overflow-y-auto p-6 bg-muted/20">
              {children}
            </main>

            {/* Footer Component */}
            <Footer />
            
          </div>
        </div>
      </TooltipProvider>
    </SidebarProvider>
  )
}
