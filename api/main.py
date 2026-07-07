"""
FastAPI Backend for the Supply Chain Control Tower.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

# Add parent directory to path so we can import src
#sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.state_manager import get_all_pending, get_pending, remove_pending
from src.agents.text_to_query_node import answer_question

from src.main import build_graph
#from src.agents.text_to_query import text_to_query_node,generate_sql
#from src.agents.query_agent import 

app = FastAPI(title="Supply Chain Control Tower API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001"
    ], # Added both
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# --- Endpoints ---

@app.get("/api/pending-actions")
async def get_pending_actions():
    """Fetches all paused LangGraph threads for the UI."""
    pending = get_all_pending()
    return pending

class ApproveRequest(BaseModel):
    thread_id: str
    action: str = "approve"  # Default to approve

# class ChatRequest(BaseModel):
#     message: str

class ChatRequest(BaseModel):
    thread_id: str
    message: str

class ChatResponse(BaseModel):  
    reply: str



@app.post("/api/approve-action")
async def approve_action(request: ApproveRequest):
    """Resumes a paused LangGraph thread with human approval."""
    thread_id = request.thread_id
    action = request.action
    state = get_pending(thread_id)
    
    if not state:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    if action == "reject":
        print(f"\n🚫 API: Thread {thread_id} REJECTED by user.")
        remove_pending(thread_id)
        return {"status": "success", "message": "Order Rejected"}
    
    print(f"\n API: Resuming thread {thread_id} with APPROVAL...")
    
    app_graph = build_graph()
    config = {"configurable": {"thread_id": thread_id}}
    
    # Update state to indicate approval
    app_graph.update_state(config, {"human_approved": True, "human_feedback": "Approved via UI"})
    
    # Resume the graph (it will run the Executor node)
    for event in app_graph.stream(None, config, stream_mode="updates"):
        pass # Let it run to completion
        
    # Clean up
    remove_pending(thread_id)
    print(f"✅ API: Thread {thread_id} completed and removed from queue.")
    
    return {"status": "success", "message": "Purchase Order Executed"}

# POST endpoint to receive the user input and return a message

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Resumes a paused LangGraph thread with human approval."""
    print(f"Received thread_id: {request.thread_id}")
    print(f"Received message: {request.message}")
    config = {"configurable": {"thread_id": request.thread_id}}
    response_request = answer_question(request.message, config)
    return {"reply":response_request}


# def generate_chat(message:str)->str:
#         return f"You asked: '{message}'. This is a dummy response - later, LangGraph will handle this!"
