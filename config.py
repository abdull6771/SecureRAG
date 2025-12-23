import os
from dataclasses import dataclass

@dataclass
class AppConfig:
    # Model Settings
    MODEL_NAME: str = "gpt-4o"
    TEMPERATURE: float = 0.0
    
    # RAG Settings
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    K_RETRIEVAL: int = 3
    
    # Paths
    VECTOR_STORE_PATH: str = "faiss_index"
    DOCS_PATH: str = "./documents"
    
    # OpenAI Key (Ensure this is set in environment)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

config = AppConfig()

if not config.OPENAI_API_KEY:
    print("WARNING: OPENAI_API_KEY not found in environment variables.")