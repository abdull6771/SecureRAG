import os
import structlog
import logging
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure structured logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=False
)

logger = structlog.get_logger()

@dataclass
class AppConfig:
    # Model Settings
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gpt-4o")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.0"))
    
    # RAG Settings
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    K_RETRIEVAL: int = int(os.getenv("K_RETRIEVAL", "3"))
    
    # Paths
    VECTOR_STORE_PATH: str = os.getenv("VECTOR_STORE_PATH", "faiss_index")
    DOCS_PATH: str = os.getenv("DOCS_PATH", "./documents")
    
    # OpenAI Key
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # API Settings
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_KEY: str = os.getenv("API_KEY", "")
    
    # Redis Configuration
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "app.log")
    
    # Guardrails
    ENABLE_TOXICITY_CHECK: bool = os.getenv("ENABLE_TOXICITY_CHECK", "true").lower() == "true"
    ENABLE_PII_DETECTION: bool = os.getenv("ENABLE_PII_DETECTION", "true").lower() == "true"
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))

config = AppConfig()

if not config.OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY not found in environment variables")
else:
    logger.info("Configuration loaded successfully", 
                model=config.MODEL_NAME, 
                chunk_size=config.CHUNK_SIZE)