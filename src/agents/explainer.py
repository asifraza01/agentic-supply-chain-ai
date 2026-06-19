"""
Explainer Agent: Generates a natural language proposal for the human.
This agent uses the LLM to synthesize the data into a clear recommendation.
"""

from typing import Dict, Any
from langchain_groq import ChatGroq
from src.state import SupplyChainState
import os


def explainer_node(state: SupplyChainState) -> Dict[str, Any]:
    """
    Generate a clear, natural language proposal for human review.
    """
    print("\n💬 [EXPLAINER] Drafting proposal...")
    
    try:
        # Check if we have the calculation
        if not state.get('reorder_calculation'):
            return {
                "error": "Cannot explain: Missing reorder calculation"
            }
         
         # Initialize Groq LLM
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        
        # Gather all the data
        # Gather all the data
        inventory = state['inventory_data']
        velocity = state['sales_velocity_data']
        reorder = state['reorder_calculation']
        
        # 🚀 NEW: Get the contract context from Qdrant
        contract_context = state.get('contract_context', "No specific contract details found.")

        
        # Build the prompt
        prompt = f"""You are a senior supply chain AI assistant. Generate a clear, professional proposal for a human supply chain manager.

CONTEXT:
- Store ID: {state['store_id']}
- Product: {inventory['product_name']} (SKU: {state['sku']})

CURRENT SITUATION:
- Current stock: {inventory['current_stock']} units (Reorder point: {inventory['reorder_point']})
- Daily sales velocity: {velocity['daily_velocity']} units/day (Trend: {velocity['trend']})

SUPPLIER CONTRACT & SLA RULES (Retrieved from Qdrant):
{contract_context}

CALCULATION:
- Recommended order: {reorder['recommended_order_quantity']} units
- Math reasoning: {reorder['reasoning']}

TASK:
Write a concise, professional proposal (3-4 sentences) that:
1. States the problem clearly.
2. Recommends the order quantity.
3. EXPLICITLY references the supplier contract rules (e.g., lead times, MOQs, or SLA penalties) to justify the decision.
4. Sounds confident and data-driven.

Be direct and factual."""

        # Generate the proposal
        response = llm.invoke(prompt)
        proposal = response.content
        
        # Calculate confidence (simple heuristic based on data quality)
        confidence = 0.85
        if velocity['trend'] == 'increasing':
            confidence = 0.90  # Higher confidence when trend is clear
        if velocity['daily_velocity'] == 0:
            confidence = 0.60  # Lower confidence with no sales data
        
        print("   ✓ Proposal generated")
        print(f"   ✓ Confidence: {confidence:.0%}")
        
        return {
            "proposal": proposal,
            "confidence": confidence
        }
    
    except Exception as e:
        return {
            "error": f"Explainer failed with exception: {str(e)}"
        }