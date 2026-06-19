"""
RAG Setup: Ingests supplier contracts into Qdrant Vector Database.
Uses StorageContext to guarantee data is flushed to the DB.
"""
import os
from qdrant_client import QdrantClient
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.fastembed import FastEmbedEmbedding

# 1. Initialize Qdrant Client
QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "supplier_contracts"
client = QdrantClient(url=QDRANT_URL)

# 2. Set the Embedding Model
Settings.embed_model = FastEmbedEmbedding(model_name="BAAI/bge-small-en-v1.5")

def ingest_contracts():
    print("📂 Checking Qdrant for existing contracts...")
    
    # Delete existing collection to ensure a clean slate for testing
    if client.collection_exists(collection_name=COLLECTION_NAME):
        print(f"⚠️  Collection '{COLLECTION_NAME}' exists. Deleting to refresh...")
        client.delete_collection(collection_name=COLLECTION_NAME)

    print("📥 Loading documents from data/contracts/...")
    documents = SimpleDirectoryReader("data/contracts").load_data()
    print(f"   Found {len(documents)} documents.")

    print(" Generating embeddings and uploading to Qdrant...")
    
    # 🚨 CRITICAL FIX: Use StorageContext to force LlamaIndex to push to Qdrant
    vector_store = QdrantVectorStore(client=client, collection_name=COLLECTION_NAME)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    # Create the index and explicitly pass the storage_context
    index = VectorStoreIndex.from_documents(
        documents, 
        storage_context=storage_context,
        show_progress=True
    )
    
    # 3. Verify the data actually made it into Qdrant
    collection_info = client.get_collection(collection_name=COLLECTION_NAME)
    
    print("\n" + "="*60)
    print("✅ SUCCESSFULLY INGESTED CONTRACTS INTO QDRANT!")
    print("="*60)
    print(f"   Collection Name: {COLLECTION_NAME}")
    print(f"   Total Vectors Stored: {collection_info.points_count}")
    print("="*60)

if __name__ == "__main__":
    ingest_contracts()