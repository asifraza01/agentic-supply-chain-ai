#from qdrant_client import QdrantClient
#from llama_index.core import VectorStoreIndex
#from llama_index.vector_stores.qdrant import QdrantVectorStore
import sys
print(sys.path)
import sqlite3
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import os
from langchain_core.messages import SystemMessage, HumanMessage
from typing import Dict, Any
#from text_raq_query import TextToQueryState,intent_router
from typing import TypedDict, Optional, List, Dict, Any, Annotated
from langgraph.graph.message import add_messages
# Import the compiled graph runtime instance
#from src.agents.chat_app_graph import supply_chain_agent


import os
import sqlite3
from typing import TypedDict, Optional, List, Dict, Any, Annotated
from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

from pydantic import BaseModel, Field
#sys.path.insert(0, str(Path(__file__).parent.parent))
# Add parent directory to path so we can import src
#sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#from src.tools.rag_tools import search_supplier_contracts
"""
RAG Tools: Functions that the LangGraph Agent can call to search contracts.
"""
from qdrant_client import QdrantClient
from llama_index.core import VectorStoreIndex, Settings
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.core.tools import FunctionTool

# 🚨 CRITICAL FIX: Force LlamaIndex to use FastEmbed instead of defaulting to OpenAI
Settings.embed_model = FastEmbedEmbedding(model_name="BAAI/bge-small-en-v1.5")

QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "supplier_contracts"
client = QdrantClient(url=QDRANT_URL)


"""
RAG Tools: Functions that the LangGraph Agent can call to search contracts.
"""

load_dotenv()

class TextToQueryState(TypedDict):
    """
    The unified state layout flowing through the 3-Way Supply Chain Agent Graph.
    """
    messages: Annotated[list, add_messages]  # Stores conversation logs natively
    intent_route: str                       # Classified path: "INVENTORY_LOOKUP", "AGENT_AUDIT", "CONTRACT_RAG"
    schemas_info: Optional[List[str]]       # SQLite table parameters
    sql_query_from_ai: Optional[str]        # Generated SQL query string
    raw_rows: Optional[List[Dict[str, Any]]]# Row results returned from SQLite execution
    raw_cols: Optional[List[str]]           # Column names returned from SQLite execution
    contract_context: Optional[str]         # Context snippets extracted from Qdrant vector database
    data_found: bool                        # The Defensive Guardrail: False flags an empty data state
    final_ai_reply: Optional[str]           # Grounded response sent back to the Next.js UI


llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.1, # Drop temperature slightly for precise classification
    max_tokens=50,   # Routing results are short, saving token resources
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# Ensure po_decisions schema information is known to the schema context
PO_DECISIONS_SCHEMA = """
Table: po_decisions, Columns: [
    (0, 'id', 'INTEGER', 1, None, 1),
    (1, 'thread_id', 'VARCHAR(100)', 1, None, 0),
    (2, 'po_number', 'VARCHAR(50)', 0, None, 0),
    (3, 'sku', 'VARCHAR(50)', 0, None, 0),
    (4, 'store_id', 'INTEGER', 0, None, 0),
    (5, 'quantity', 'INTEGER', 0, None, 0),
    (6, 'decision', 'VARCHAR(20)', 1, None, 0),
    (7, 'decided_at', 'DATETIME', 0, None, 0),
    (8, 'decided_by', 'VARCHAR(100)', 0, None, 0),
    (9, 'rejection_reason', 'TEXT', 0, None, 0),
    (10, 'investigator_context', 'TEXT', 0, None, 0),
    (11, 'optimizer_calculation', 'TEXT', 0, None, 0),
    (12, 'explainer_proposal', 'TEXT', 0, None, 0),
    (13, 'confidence_score', 'REAL', 0, None, 0)
]
"""
INVENTORY_SCHEMA ="""
    Table: inventory, Columns: [store_id (INTEGER), sku (VARCHAR(50)), product_name (VARCHAR(200)), current_stock (INTEGER), reorder_point (INTEGER), location (VARCHAR(100))]
    Table: sales_history, Columns: [store_id (INTEGER), sku (VARCHAR(50)), sale_date (DATETIME), units_sold (INTEGER)]
    Table: purchase_orders, Columns: [po_number (VARCHAR(50)), store_id (INTEGER), sku (VARCHAR(50)), quantity (INTEGER), status (VARCHAR(20)), created_at (DATETIME), approved_by (VARCHAR(100))]
    """


# Define a tight validation schema to enforce exact router output values
class RouteClassification(BaseModel):
    route: str = Field(
        description="The target category path. Must be exactly 'INVENTORY_LOOKUP', 'AGENT_AUDIT', or 'CONTRACT_RAG'."
    )

def intent_router(state: TextToQueryState):
    print("\n--- Node: Intent Router ---")
    user_msg = state["messages"][-1].content
    
    # Construct a highly constrained routing directive
    system_prompt = """You are a senior supply chain routing supervisor. 
    Classify the incoming executive question into EXACTLY one of three category pathways:
    
    1. INVENTORY_LOOKUP: Queries searching for current stock levels, units sold, or reorder points in specific tables (e.g., "Is Store 101 low on eggs?", "Show me units sold for SKU-APP-101").
    2. AGENT_AUDIT: Questions asking 'WHY' a purchase order was created, looking for AI reasoning parameters, or inquiring about pre-computed decisions (e.g., "Why did you create PO-LNGRPH-8291?", "Explain why this order is locked").
    3. CONTRACT_RAG: Questions referencing supplier contracts, vendor agreements, lead times, minimum order volume constraints, SLAs, or legal penalties (e.g., "What is the lead time for organic milk from our contract?", "Does this quantity violate our SLA?").
    
    Respond ONLY with the raw classification string name. Do not include markdown, spaces, punctuation, or any accompanying conversational text."""

    # Bind structural constraint directly to your Groq LLM instance
    structured_llm = llm.with_structured_output(RouteClassification)
    
    try:
        response = structured_llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_msg)
        ])
        classified_route = response.route.strip().upper()
    except Exception as e:
        print(f"Router fallback triggered due to parsing: {e}")
        # Dynamic keyword-matching fallback safety net if structured window fails
        lower_msg = user_msg.lower()
        if any(w in lower_msg for w in ["contract", "sla", "agreement", "vendor", "lead time", "penalty"]):
            classified_route = "CONTRACT_RAG"
        elif any(w in lower_msg for w in ["why", "audit", "reason", "decision", "explainer"]):
            classified_route = "AGENT_AUDIT"
        else:
            classified_route = "INVENTORY_LOOKUP"

    print(f" -> Routing Target Evaluated As: {classified_route}")
    return {"intent_route": classified_route}


def create_sql_query(state: TextToQueryState):
    print("\n--- Node: Create SQL Query ---")
    route = state["intent_route"]
    user_msg = state["messages"][-1].content
    
    # 1. Tailor database metadata dynamically based on routing flags
    if route == "AGENT_AUDIT":
        schema_context = PO_DECISIONS_SCHEMA
        instruction = "You are looking at autonomous agent records. Write a SELECT query targeting the 'po_decisions' table to fetch reasoning text column values (like explainer_proposal or investigator_context) matching the requested filters."
    else:
        # Fallback to your generic inventory schemas
        schema_context = state.get("schemas_info", INVENTORY_SCHEMA)
        instruction = "You are looking at standard store inventory structures. Write a SELECT query targeting inventory, sales_history, or purchase_orders."

    system_prompt = f"""You are an elite SQLite data analyst.
    Database Schema Layout:
    {schema_context}
    
    CRITICAL INSTRUCTION: {instruction}
    
    Generate ONLY the raw executable SQL SELECT statement string text. 
    Do not include markdown tags, block wrapping (```sql), explanation text, or assumptions. Output the raw text string directly."""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_msg)
    ])
    
    clean_query = response.content.replace("```sql", "").replace("```", "").strip()
    print(f" -> Generated SQL Query: {clean_query}")
    return {"sql_query_from_ai": clean_query}


def execute_sql_query(state: TextToQueryState):
    print("\n--- Node: Execute SQL Query ---")
    query = state.get("sql_query_from_ai")
    if not query:
        return {"raw_rows": [], "raw_cols": []}
        
    conn = sqlite3.connect(os.getenv("sqllightlink"))
    cursor = conn.cursor()
    
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        dict_rows = [dict(zip(columns, r)) for r in rows]
        print(f" -> SQLite Execution Successful. Returned {len(dict_rows)} record rows.")
    except Exception as e:
        print(f" ❌ SQLite Query Execution Failed: {e}")
        dict_rows = []
        columns = []
        
    conn.close()
    return {"raw_cols": columns, "raw_rows": dict_rows}

def run_contract_rag(state: TextToQueryState):
    print("\n--- Node: Contract Qdrant RAG ---")
    user_msg = state["messages"][-1].content
    
    # Instantiate runtime vector store using your exact parameter variables
    #client = QdrantClient(url="http://localhost:6333")
    vector_store = QdrantVectorStore(client=client, collection_name=COLLECTION_NAME)
    #index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
    index = VectorStoreIndex.from_vector_store(
        vector_store, 
        embed_model=Settings.embed_model
    )
    print(" -> Scanning supplier_contracts collection points via bge-small embedding vectors...")
    retriever = index.as_retriever(similarity_top_k=2)
    matched_nodes = retriever.retrieve(user_msg)
    
    # Gather matching snippet contexts cleanly
    context_fragments = []
    for idx, node in enumerate(matched_nodes, 1):
        score = node.get_score()
        content = node.node.get_content().strip()
        context_fragments.append(f"[Snippet #{idx} | Rel. Score: {score:.2f}]:\n{content}")
        
    combined_context = "\n\n".join(context_fragments)
    print(f" -> Vector search complete. Retrieved {len(context_fragments)} contract blocks.")
    #contract_context = search_supplier_contracts(user_msg)
    return {"contract_context": combined_context}




def check_data_presence_guardrail(state: TextToQueryState):
    print("\n--- Node: Data Presence Guardrail Check ---")
    route = state.get("intent_route")
    
    # Check SQL-based pathways
    if route in ["INVENTORY_LOOKUP", "AGENT_AUDIT"]:
        rows = state.get("raw_rows")
        # If the database returns an empty list, flag it as a data missing condition
        if not rows or len(rows) == 0:
            print(" ⚠️  CRITICAL: SQLite query returned 0 results. Activating Defensive Guardrail.")
            return {"data_found": False}
            
    # Check Vector Store pathways
    elif route == "CONTRACT_RAG":
        context = state.get("contract_context")
        if not context or not context.strip():
            print(" ⚠️  CRITICAL: Qdrant search returned no text snippets. Activating Defensive Guardrail.")
            return {"data_found": False}
            
    print(" ✅ Guardrail Passed: Valid data presence verified in workflow state.")
    return {"data_found": True}


def final_ai_reply(state: TextToQueryState):
    print("\n--- Node: Context-Aware Final AI Reply ---")
    
    user_msg = state["messages"][-1].content
    route = state.get("intent_route")
    data_found = state.get("data_found", True)

    # 🛑 DEFENSIVE FIREWALL TRIGGERED: Immediately halt and prevent hallucinations
    if not data_found:
        reply = f"I evaluated our supply chain database records for your query ('{user_msg}'), but no matching entries were found in our live tables or supplier contracts. Please verify the target SKU, PO number, or system parameters."
        return {"final_ai_reply": reply}

    # 🟢 ROUTE 1: Traditional Inventory metrics compiler
    if route == "INVENTORY_LOOKUP":
        db_data = state.get("raw_rows")
        system_prompt = f"""You are a senior supply chain metrics analyst. 
        Synthesize the raw database row data to answer the user's business question.
        
        CRITICAL CONSTRAINT: Base your response ONLY on the factual database numbers provided below. 
        Do not make assumptions, invent numbers, or add hypothetical store calculations.
        
        DATABASE RESPONSE DATA: {db_data}"""
        
        prompt_content = f"Answer the user's question: '{user_msg}' clearly and concisely using the metrics data above."

    # 🟣 ROUTE 2: Autonomous Agent Audit trail compiler
    elif route == "AGENT_AUDIT":
        audit_data = state.get("raw_rows")
        system_prompt = f"""You are an executive operations auditor. 
        The user is asking about an autonomous action taken by a LangGraph AI background agent.
        Explain the workflow context clearly using the pre-computed audit rows provided.
        
        CRITICAL CONSTRAINT: State the agent's explanation context verbatim. Do not compute new math parameters.
        
        PO_DECISIONS LOG RECORDS: {audit_data}"""
        
        prompt_content = f"Provide a transparent breakdown explaining: '{user_msg}' using the logs above."

    # 🟢 ROUTE 3: Legal Supplier Contract RAG compiler
    else:
        rag_context = state.get("contract_context")
        system_prompt = f"""You are a corporate supply chain procurement manager. 
        Analyze the provided supplier contract text snippets to address the legal or service-level query.
        
        CRITICAL CONSTRAINT: Rely ONLY on the contract text below. If the information isn't present, say so.
        
        EXTRACTED CONTRACT FRAGMENTS:
        {rag_context}"""
        
        prompt_content = f"Answer the vendor contract question: '{user_msg}' using the legal context provided above."

    # Invoke your Llama 3.3 instance using the tailored system template configuration
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=prompt_content)
    ])
    
    print(" -> Final Business Response Compiled Successfully.")
    return {"final_ai_reply": response.content}

# =========================================================================
# 1. STATE CLEARING GUARD NODE
# =========================================================================
def input_init_and_flush(state:TextToQueryState):
    print("\n" + "="*50)
    print("🔄 [STARTING NEW GRAPH TURN] Flushed Stale Data Contexts")
    print("="*50)
    
    # We return None for all data slots to clear out variables from the previous turn,
    # preventing old SQL rows from lingering and corrupting new questions.
    return {
        "intent_route": "",
        "sql_query_from_ai": None,
        "raw_rows": None,
        "raw_cols": None,
        "contract_context": None,
        "data_found": True
    }

# =========================================================================
# 2. CONDITIONAL EDGE ROUTER DEFINITIONS
# =========================================================================
def route_by_intent(state: TextToQueryState) -> str:
    """
    Evaluates the intent_route saved by the intent_router node and
    directs the graph engine down the matching architectural pathway.
    """
    route = state.get("intent_route", "INVENTORY_LOOKUP")
    
    if route == "CONTRACT_RAG":
        return "contract_rag_path"
    elif route == "AGENT_AUDIT":
        return "agent_audit_path"
    else:
        return "inventory_lookup_path"

# =========================================================================
# 3. GRAPH COMPILATION WORKSPACE
# =========================================================================
builder = StateGraph(TextToQueryState)

# Add all pipeline action nodes
builder.add_node("input_init", input_init_and_flush)
builder.add_node("router", intent_router)
builder.add_node("createsql", create_sql_query)
builder.add_node("exesql", execute_sql_query)
builder.add_node("contract_rag", run_contract_rag)
builder.add_node("guardrail", check_data_presence_guardrail)
builder.add_node("final_reply", final_ai_reply)

# Define static structural flows
builder.add_edge(START, "input_init")
builder.add_edge("input_init", "router")

# Define the Three-Way Conditional Router routing decisions
builder.add_conditional_edges(
    "router",
    route_by_intent,
    {
        "inventory_lookup_path": "createsql",  # Path A: Standard SQL
        "agent_audit_path": "createsql",       # Path B: po_decisions Audit SQL
        "contract_rag_path": "contract_rag"    # Path C: Qdrant Vector RAG
    }
)

# Connect execution endpoints down to the defensive guardrail firewall

builder.add_edge("createsql", "exesql")
builder.add_edge("exesql", "guardrail")
builder.add_edge("contract_rag", "guardrail")

# Direct the guardrail to compile the final formatted response text
builder.add_edge("guardrail", "final_reply")
builder.add_edge("final_reply", END)

# Initialize an in-memory checkpointer session repository
memory_layer = MemorySaver()
supply_chain_agent = builder.compile(checkpointer=memory_layer)

print("🎉 Agentic Supply Chain Graph Compiled Successfully with State Guards.")


def answer_question_v2(question: str,config: dict) -> str:
#     """Convenient wrapper – returns the final markdown answer."""
    result = supply_chain_agent.invoke({"messages": [HumanMessage(content=question)]}, config=config)
     #return result["final_text"]
     #return
     #return mm["final_ai_reply"] 
     #return {"reply": result.final_ai_reply}
    print("Full result:", result)  # ← See the entire dictionary
    print("Final reply:", result["final_ai_reply"])  # ← See just the answer
    return result["final_ai_reply"]
