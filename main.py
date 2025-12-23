import json
import os
from ingestion import KnowledgeBase
from engine import SecureRAGEngine
from config import config, logger

# Ensure env var is set (or set it here for testing)
# os.environ["OPENAI_API_KEY"] = "sk-..."

def main():
    logger.info("Initializing Secure RAG System")
    
    # 1. Initialize Knowledge Base
    kb = KnowledgeBase()
    
    # Toggle force_rebuild=True if you added new documents
    vectorstore = kb.get_vector_store(force_rebuild=False)
    
    # 2. Initialize Engine with memory
    rag_engine = SecureRAGEngine(vectorstore, enable_memory=True)
    
    # 3. Interactive Loop
    logger.info("System Ready. Type 'exit' to quit.")
    print("\n✅ System Ready. Type 'exit' to quit.\n")
    
    session_id = "cli-session"
    
    while True:
        query = input("User Query: ")
        if query.lower() in ['exit', 'quit']:
            logger.info("Shutting down")
            break
            
        result = rag_engine.query(query, session_id=session_id)
        
        # Display Result
        print("\n--- 🛡️ Guarded Response ---")
        print(json.dumps(result, indent=2))
        print("---------------------------\n")

if __name__ == "__main__":
    main()