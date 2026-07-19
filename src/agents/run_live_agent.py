import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq

# Import the compiled graph runtime instance
from chat_app_graph import supply_chain_agent

load_dotenv()

# Bind the target model execution weights for the runner script environment
llm_instance = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.2,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

import text_query
text_query.llm = llm_instance

def run_production_test_suite():
  # Configure a persistent configuration thread session ID
    config = {"configurable": {"thread_id": "executive_session_999"}}

    print("\n🚀 [QUERY 1: Single Target Look-Up]")
    msg1 = "Show me current stock levels for SKU-100 at store 1"
    res1 = supply_chain_agent.invoke({"messages": [HumanMessage(content=msg1)]}, config=config)
    print(f"\033[92mFinal Answer 1:\033[0m {res1['final_ai_reply']}")

    print("\n🚀 [QUERY 2: Multi-Store Grouping Calculation on Same Thread]")
    msg2 = "Show me total stock levels for SKU-100 in all stores group by each store"
    res2 = supply_chain_agent.invoke({"messages": [HumanMessage(content=msg2)]}, config=config)
    print(f"\033[92mFinal Answer 2:\033[0m {res2['final_ai_reply']}")

if __name__ == "__main__":
    run_production_test_suite()
