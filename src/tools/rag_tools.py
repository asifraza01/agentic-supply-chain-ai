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

def search_supplier_contracts(query: str) -> str:
    """
    Search supplier contracts, SLAs, and historical reports for specific information.
    Use this to find lead times, penalty clauses, MOQs, or past incident root causes.
    
    Args:
        query: The specific question or topic to search for (e.g., 'SKU-100 lead time and penalties').
    """
    print(f"   🔍 [RAG TOOL] Searching contracts for: '{query}'")
    
    client = QdrantClient(url=QDRANT_URL)
    vector_store = QdrantVectorStore(client=client, collection_name=COLLECTION_NAME)
    
    # Explicitly pass the embed_model to prevent OpenAI fallback
    index = VectorStoreIndex.from_vector_store(
        vector_store, 
        embed_model=Settings.embed_model
    )
    
    # Retrieve the top 2 most relevant chunks
    retriever = index.as_retriever(similarity_top_k=2)
    nodes = retriever.retrieve(query)
    
    if not nodes:
        return "No relevant contract information found."
    
    # Format the results nicely for the LLM
    context = "\n\n---\n\n".join([node.text for node in nodes])
    return context

# Wrap it in a LangChain/LlamaIndex Tool format
rag_search_tool = FunctionTool.from_defaults(fn=search_supplier_contracts)