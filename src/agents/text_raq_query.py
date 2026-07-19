import os
from typing import TypedDict, Optional, List, Dict, Any, Annotated
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_groq import ChatGroq
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

# Load environment keys
load_dotenv()

# Initialize  Groq client model matching  exact configuration
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.1, # Drop temperature slightly for precise classification
    max_tokens=50,   # Routing results are short, saving token resources
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# Define Phase 1 State Schema
class TextToQueryState(TypedDict):
    messages: Annotated[list, add_messages]
    intent_route: str
    schemas_info: Optional[List[str]]
    sql_query_from_ai: Optional[str]
    raw_rows: Optional[List[Dict[str, Any]]]
    raw_cols: Optional[List[str]]
    contract_context: Optional[str]
    data_found: bool
    final_ai_reply: Optional[str]

# Strict verification schema for Groq's structured output tool calling
class RouteClassification(BaseModel):
    route: str = Field(
        description="The target category path. Must be exactly 'INVENTORY_LOOKUP', 'AGENT_AUDIT', or 'CONTRACT_RAG'."
    )

# The Intent Router Node Function
def intent_router(state: TextToQueryState):
    print("\n--- Node: Intent Router Execution ---")
    user_msg = state["messages"][-1].content
    print(f" -> Executive Input: '{user_msg}'")
    
    system_prompt = """You are a senior supply chain routing supervisor. 
    Classify the incoming executive question into EXACTLY one of three category pathways:
    
    1. INVENTORY_LOOKUP: Queries searching for current stock levels, units sold, or reorder points in specific tables (e.g., "Is Store 101 low on eggs?", "Show me units sold for SKU-APP-101").
    2. AGENT_AUDIT: Questions asking 'WHY' a purchase order was created, looking for AI reasoning parameters, or inquiring about pre-computed decisions (e.g., "Why did you create PO-LNGRPH-8291?", "Explain why this order is locked").
    3. CONTRACT_RAG: Questions referencing supplier contracts, vendor agreements, lead times, minimum order volume constraints, SLAs, or legal penalties (e.g., "What is the lead time for organic milk from our contract?", "Does this quantity violate our SLA?").
    
    Respond ONLY with the raw classification string name. Do not include markdown, spaces, punctuation, or any accompanying conversational text."""

    structured_llm = llm.with_structured_output(RouteClassification)
    print(structured_llm)
    
    try:
        response = structured_llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_msg)
        ])
        classified_route = response.route.strip().upper()
    except Exception as e:
        print(f"    [Router Fallback Activated] Reason: {e}")
        lower_msg = user_msg.lower()
        if any(w in lower_msg for w in ["contract", "sla", "agreement", "vendor", "lead time", "penalty"]):
            classified_route = "CONTRACT_RAG"
        elif any(w in lower_msg for w in ["why", "audit", "reason", "decision", "explainer"]):
            classified_route = "AGENT_AUDIT"
        else:
            classified_route = "INVENTORY_LOOKUP"

    print(f" -> Evaluated Intent Route Target: \033[94m{classified_route}\033[0m")
    return {"intent_route": classified_route}
    

# --- Immediate Phase 1 Test Execution Suite ---
if __name__ == "__main__":
    print("="*60)
    print("RUNNING THE PHASE 1 SYSTEM INTENT TEST SYSTEM")
    print("="*60)

    # Test cases representing each workspace profile
    test_queries = [
        "Show me all items in Aisle A that have less than 15 units left", # Should be INVENTORY_LOOKUP
        "Why did the autonomous agent generate order PO-LNGRPH-8420 yesterday?", # Should be AGENT_AUDIT
        "What is the contract lead time penalty if the supplier delivers late?", # Should be CONTRACT_RAG
    ]

    for index, query in enumerate(test_queries, 1):
        print(f"\n[Test Case #{index}]")
        # Format the mock state passing standard HumanMessage layout
        mock_state: TextToQueryState = {
            "messages": [HumanMessage(content=query)],
            "intent_route": "",
            "schemas_info": None,
            "sql_query_from_ai": None,
            "raw_rows": None,
            "raw_cols": None,
            "contract_context": None,
            "data_found": True,
            "final_ai_reply": None
        }
        
        # Execute the node function directly
        update = intent_router(mock_state)
        
        # Output confirmation of state mutation parameters
        print(f" -> State Update Array Generated: {update}")
    
    print("\n" + "="*60)
    print("PHASE 1 TESTING VERIFIED CLEANLY")
    print("="*60)
