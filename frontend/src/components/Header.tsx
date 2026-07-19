// component/Header.tsx
"use client"

import { SidebarTrigger } from "@/components/ui/sidebar"
import { Bell, User } from "lucide-react"
import { Button } from "@/components/ui/button"

export function Header() {
  return (
    <header className="flex h-14 items-center justify-between border-b px-6 bg-card shrink-0">
      <div className="flex items-center gap-4">
        <SidebarTrigger />
        <span className="text-sm font-medium text-muted-foreground">Workspace</span>
      </div>
      
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="icon" className="h-8 w-8">
          <Bell className="h-4 w-4" />
        </Button>
        <Button variant="ghost" size="icon" className="h-8 w-8 rounded-full border">
          <User className="h-4 w-4" />
        </Button>
      </div>
    </header>
  )
}
