"""
State manager using SQLite to share LangGraph state between processes.
"""
import sqlite3
import json

#CHECKPOINT_DB = "langgraph_checkpoints.db"
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
CHECKPOINT_DB = PROJECT_ROOT / "langgraph_checkpoints.db"

def get_connection():
    return sqlite3.connect(CHECKPOINT_DB, check_same_thread=False)

def add_pending(thread_id: str, state: dict):
    """Mark a thread as pending approval (we'll use a simple table for this)."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create pending_approvals table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pending_approvals (
            thread_id TEXT PRIMARY KEY,
            state_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insert or update the pending state
    state['thread_id'] = thread_id
    state_json = json.dumps(state, default=str)
    
    cursor.execute("""
        INSERT OR REPLACE INTO pending_approvals (thread_id, state_json)
        VALUES (?, ?)
    """, (thread_id, state_json))
    
    conn.commit()
    conn.close()
    print(f"💾 Saved thread {thread_id} to pending_approvals table")

def get_pending(thread_id: str):
    """Get a pending state by thread_id."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT state_json FROM pending_approvals WHERE thread_id = ?
    """, (thread_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return json.loads(row[0])
    return None

def remove_pending(thread_id: str):
    """Remove a pending state."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        DELETE FROM pending_approvals WHERE thread_id = ?
    """, (thread_id,))
    
    conn.commit()
    conn.close()

def get_all_pending():
    """Get all pending states."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pending_approvals (
            thread_id TEXT PRIMARY KEY,
            state_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        SELECT state_json FROM pending_approvals
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    return [json.loads(row[0]) for row in rows]

