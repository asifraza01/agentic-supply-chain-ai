"use client"

import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { useState, useRef, useEffect } from "react"
import ReactMarkdown from 'react-markdown'

export function ChatWindow({ threadId }: { threadId: string }) {
  const [inputValue, setInputValue] = useState("")
  const [messages, setMessages] = useState<{ role: "user" | "assistant"; content: string }[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const scrollContainerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollTop = scrollContainerRef.current.scrollHeight
    }
  }, [messages, isLoading])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputValue.trim() || isLoading) return

    setError(null)
    setIsLoading(true)

    const userMessage = inputValue.trim()
    setMessages(prev => [...prev, { role: "user", content: userMessage }])
    setInputValue("")

    try {
      const res = await fetch("http://127.0.0.1:8001/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMessage, thread_id: threadId }),
      })

      if (!res.ok) {
        const errorText = await res.text()
        console.error("Server error:", errorText)
        throw new Error(`Server error: ${res.status}`)
      }

      const data = await res.json()
      if (!data.reply) throw new Error("No reply received")

      setMessages(prev => [...prev, { role: "assistant", content: data.reply }])
    } catch (error) {
      console.error("❌ Failed:", error)
      setError(error instanceof Error ? error.message : "Failed to send message")
      setMessages(prev => [...prev, { 
        role: "assistant", 
        content: "⚠️ Sorry, I encountered an error. Please try again." 
      }])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-12rem)] max-w-2xl mx-auto p-4 gap-4">
      <Card className="flex-1 flex flex-col overflow-hidden">
        <div className="border-b p-4 bg-gray-50 flex-shrink-0">
          <h3 className="font-semibold text-lg">AI Assistant</h3>
          <p className="text-xs text-gray-500">Thread: {threadId.slice(0, 8)}...</p>
        </div>

        <div 
          ref={scrollContainerRef}
          className="flex-1 overflow-y-auto overflow-x-hidden p-4"
        >
          <div className="space-y-4">
            {messages.length === 0 && (
              <div className="text-center text-gray-400 py-8">
                <p>Start a conversation by typing a message below</p>
              </div>
            )}
            
            {messages.map((msg, index) => (
              <div 
                key={index} 
                className={msg.role === "user" ? "flex justify-end" : "flex justify-start"}
              >
                <div 
                  className={
                    msg.role === "user"
                      ? "bg-blue-500 text-white rounded-lg p-3 max-w-[70%] shadow-sm break-words overflow-hidden"
                      : "bg-gray-100 text-gray-900 rounded-lg p-3 max-w-[70%] shadow-sm break-words overflow-hidden"
                  }
                >
                  {msg.role === "user" ? (
                    <p className="whitespace-pre-line break-words">{msg.content}</p>
                  ) : (
                    <div className="prose prose-sm max-w-none break-words overflow-x-hidden">
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    </div>
                  )}
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 rounded-lg p-3 shadow-sm">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        <form onSubmit={handleSubmit} className="border-t p-4 bg-white flex-shrink-0">
          <div className="flex gap-2">
            <Input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Type a message..."
              disabled={isLoading}
              className="flex-1"
            />
            <Button 
              type="submit" 
              disabled={isLoading || !inputValue.trim()}
              className="px-6"
            >
              {isLoading ? "Sending..." : "Send"}
            </Button>
          </div>
          {error && (
            <p className="text-red-500 text-sm mt-2">{error}</p>
          )}
        </form>
      </Card>
    </div>
  )
}