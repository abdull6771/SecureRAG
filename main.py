import json
import os
from ingestion import KnowledgeBase
from engine import SecureRAGEngine
from config import config

# Ensure env var is set (or set it here for testing)
# os.environ["OPENAI_API_KEY"] = "sk-..."

def main():
    print("--- 🚀 Initializing Secure RAG System ---")
    
    # 1. Initialize Knowledge Base
    kb = KnowledgeBase()
    
    # Toggle force_rebuild=True if you added new documents
    vectorstore = kb.get_vector_store(force_rebuild=True)
    
    # 2. Initialize Engine
    rag_engine = SecureRAGEngine(vectorstore)
    
    # 3. Interactive Loop
    print("\n✅ System Ready. Type 'exit' to quit.\n")
    
    while True:
        query = input("User Query: ")
        if query.lower() in ['exit', 'quit']:
            break
            
        result = rag_engine.query(query)
        
        # Display Result
        print("\n--- 🛡️ Guarded Response ---")
        print(json.dumps(result, indent=2))
        print("---------------------------\n")

if __name__ == "__main__":
    main()