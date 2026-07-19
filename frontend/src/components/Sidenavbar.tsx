// component/Sidenavbar.tsx
"use client"

import * as React from "react"
import Link from "next/link"
import { usePathname } from "next/navigation" // For tracking active tabs

import { LayoutDashboard, Users, FolderKanban, HelpCircle, MessageCircleMore } from "lucide-react"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarGroupContent,
} from "@/components/ui/sidebar" // Adjust if your shadcn folder is @/components/ui

const menuItems = [
 // { title: "Dashboard", url: "/dashboard", icon: LayoutDashboard },
 // { title: "Purchase Orders", url: "/purchase-orders", icon: FolderKanban },
  
  { title: "Action Queue", url: "/action-queue", icon: Users },
  { title: "Decisions", url: "/decisions", icon: Users },
  { title: "Chat", url: "/chat", icon: MessageCircleMore },
 // { title: "Old page", url: "/oldpage", icon: Users },
]

export function Sidenavbar() {
  const pathname = usePathname() // Get the current path for active tab highlighting
  return (
    <Sidebar variant="sidebar" collapsible="icon">
      <SidebarHeader className="border-b h-14 justify-center px-4">
        <Link href="/" className="flex items-center gap-2 font-semibold">
          <div className="flex h-6 w-6 items-center justify-center rounded bg-primary text-primary-foreground text-xs">
            App
          </div>
          <span className="group-data-[collapsible=icon]:hidden font-medium">Console</span>
        </Link>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Application</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {menuItems.map((item) =>{
                // Check if this menu option matches our current window route
                const isActive = pathname === item.url
                return (
                  <SidebarMenuItem key={item.title}>
                    <SidebarMenuButton 
                        asChild 
                        isActive={isActive}
                        tooltip={item.title}>
                      <Link href={item.url} className="flex items-center gap-2">
                        <item.icon className="h-4 w-4 shrink-0" />
                        <span className="group-data-[collapsible=icon]:hidden">{item.title}</span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                )})}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="border-t p-4">
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton asChild isActive={pathname === "/help"} tooltip="Support">
              <Link href="/help" className="flex items-center gap-2">
                <HelpCircle className="h-4 w-4" />
                <span className="group-data-[collapsible=icon]:hidden">Support</span>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  )
}
