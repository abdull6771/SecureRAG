# 🛡️ SecureRAG

**SecureRAG** is a production-grade Retrieval-Augmented Generation (RAG) system that combines **LangChain** for orchestration and **Guardrails AI** for structured output validation. This system ensures that LLM responses are always reliable, well-structured, and compliant with predefined schemas.

## 🎯 Project Overview

SecureRAG is a comprehensive RAG system with enterprise-ready features:

- **Document Intelligence**: Retrieve relevant information from your local document collection
- **Accurate Answers**: Generate precise answers using OpenAI's GPT models
- **Advanced Validation**: Validate and structure responses with Guardrails AI (toxicity, PII detection)
- **REST API**: Full-featured FastAPI web service with authentication
- **Conversation Memory**: Redis-backed multi-turn conversation tracking
- **Streaming Responses**: Real-time token streaming for better UX
- **Source Citations**: Track which documents informed each answer with confidence levels
- **Structured Logging**: Production-grade logging with structlog
- **Testing Suite**: Comprehensive unit tests for all components

## 🏗️ Architecture

```
User Query → FastAPI/CLI → Knowledge Base (FAISS) → RAG Engine → LLM Generation →
Guardrails Validation → Redis Memory → Structured Response
```

### Enhanced Architecture Features

- **Multiple Interfaces**: REST API + CLI
- **Conversation Memory**: Redis-backed with in-memory fallback
- **Streaming Support**: Real-time token generation
- **Advanced Guardrails**: Toxicity detection, PII filtering
- **Document Metadata**: Enhanced tracking and filtering

## 📁 Project Structure

### Core Files

### **`config.py`**

Enhanced configuration with environment variable support:

- **Model Settings**: GPT model selection and temperature
- **RAG Parameters**: Chunk size, overlap, and retrieval count (k)
- **Paths**: Vector store location and document directory
- **API Configuration**: Host, port, API key authentication
- **Redis Settings**: Memory backend configuration
- **Logging**: Structured logging with configurable levels
- **Guardrails**: Toxicity and PII detection settings

**Key Configurations:**

```python
MODEL_NAME: "gpt-4o"
CHUNK_SIZE: 1000
CHUNK_OVERLAP: 200
K_RETRIEVAL: 3
API_PORT: 8000
REDIS_HOST: "localhost"
ENABLE_TOXICITY_CHECK: true
ENABLE_PII_DETECTION: true
```

### **`schemas.py`**

Enhanced with advanced Guardrails validators:

- **RAGResponse**: Enforces structured JSON responses
  - `answer`: Validated response (5-1000 characters)
  - `confidence`: Categorical confidence level (high/medium/low)
  - `sources`: List of document sources used
- **Advanced Validators**:
  - `ToxicLanguage`: Detects and filters toxic content
  - `DetectPII`: Removes sensitive information (email, phone, SSN)
  - `ValidLength`: Ensures appropriate response length
- **QueryRequest**: API request schema with validation
- **DocumentUploadResponse**: Document upload response schema

### **`ingestion.py`**

Document processing with enhanced metadata:

- **KnowledgeBase Class**: Complete document pipeline
  - Loads documents (.txt, .pdf) from `./documents` directory
  - **Metadata Enhancement**: Filename, size, upload date, extension
  - **Metadata Filtering**: Filter documents by any metadata field
  - Creates FAISS vector embeddings using OpenAI
  - Saves/loads vector store for efficient reuse
  - Structured logging throughout

**New Features:**

- Enhanced document metadata tracking
- Filter documents by metadata (extension, date, size)
- Comprehensive error handling with logging

### **`engine.py`**

RAG engine with memory and streaming:

- **SecureRAGEngine Class**: Orchestrates the RAG pipeline
  - Initializes retriever, LLM, and Guardrails
  - Builds LCEL (LangChain Expression Language) chain
  - Formats retrieved documents with source citations
  - Validates LLM output against `RAGResponse` schema
- **ConversationMemory Class**: Multi-turn conversation support
  - Redis-backed storage with in-memory fallback
  - Session-based conversation tracking
  - Automatic TTL management (1 hour)
  - Context retention across queries

**Pipeline Features:**

1. Retrieve top-k relevant documents
2. Add conversation context from memory
3. Generate response via GPT-4o
4. Parse and validate with Guardrails
5. Save to conversation memory
6. Return structured JSON response

**Advanced Features:**

- `query(user_query, session_id)`: Query with memory support
- `query_stream()`: Async streaming responses
- Input validation with logging
- Error handling with fallback responses
- Session management

### **`main.py`**

Enhanced CLI with logging and memory:

- Initializes Knowledge Base and RAG Engine
- Session-based conversation tracking
- Interactive query loop with structured logging
- Displays validated JSON responses
- Graceful shutdown

### **`api.py`** ⭐ NEW

Full-featured FastAPI REST API:

- **Authentication**: API key-based security
- **CORS**: Cross-origin resource sharing support
- **Auto Documentation**: Swagger UI + ReDoc

**Endpoints:**

- `GET /` - Health check
- `GET /health` - Detailed system health
- `POST /query` - Query with optional memory
- `POST /query/stream` - Streaming responses
- `POST /documents/upload` - Upload documents
- `DELETE /documents/{filename}` - Delete documents
- `GET /documents` - List all documents
- `POST /memory/clear/{session_id}` - Clear conversation history

### Configuration Files

### **`requirements.txt`** ⭐ NEW

Complete dependency list:

- Core: LangChain, Guardrails AI, OpenAI
- API: FastAPI, Uvicorn
- Storage: FAISS, Redis
- Logging: Structlog
- Testing: Pytest, pytest-asyncio
- Development: Black, Flake8, Mypy

### **`.env.example`** ⭐ NEW

Environment variable template:

- OpenAI API key
- Model configuration
- Redis settings
- API configuration
- Logging settings
- Guardrails flags

### **`.gitignore`** ⭐ NEW

Comprehensive ignore patterns:

- Python artifacts
- Virtual environments
- API keys and secrets
- Vector stores and indexes
- Logs and cache
- IDE files

### Testing Suite ⭐ NEW

### **`tests/`**

Complete test coverage:

- `test_config.py` - Configuration validation
- `test_ingestion.py` - Document loading and metadata
- `test_schemas.py` - Pydantic schema validation
- `test_engine.py` - Conversation memory tests
- `test_api.py` - API endpoint testing

Run tests:

```bash
pytest tests/ -v
pytest tests/ --cov=. --cov-report=html
```

## 🚀 Getting Started

### Quick Start

1. **Clone the repository:**

```bash
git clone https://github.com/abdull6771/SecureRAG.git
cd SecureRAG
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Configure environment:**

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

4. **Add documents:**
   Place your .txt or .pdf files in the `./documents` directory.

5. **Run the application:**

**Option A: CLI Interface**

```bash
python main.py
```

**Option B: REST API**

```bash
python api.py
# API will be available at http://localhost:8000
# Documentation at http://localhost:8000/docs
```

### Prerequisites

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install langchain langchain-openai langchain-community
pip install guardrails-ai faiss-cpu pypdf pydantic
pip install fastapi uvicorn python-dotenv structlog redis pytest
```

## 🔌 API Usage

### Start the API Server

```bash
python api.py
# Or with uvicorn:
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

### API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Example API Calls

**Query with conversation memory:**

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "query": "What is machine learning?",
    "session_id": "user123"
  }'
```

**Streaming query:**

```bash
curl -X POST http://localhost:8000/query/stream \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "query": "Explain RAG systems",
    "stream": true
  }'
```

**Upload document:**

```bash
curl -X POST http://localhost:8000/documents/upload \
  -H "X-API-Key: your-api-key" \
  -F "file=@document.pdf"
```

**List documents:**

```bash
curl -X GET http://localhost:8000/documents \
  -H "X-API-Key: your-api-key"
```

**Clear conversation memory:**

```bash
curl -X POST http://localhost:8000/memory/clear/user123 \
  -H "X-API-Key: your-api-key"
```

## 🔄 Usage Flow

### CLI Usage

1. **First Run**: Builds FAISS vector store from documents
2. **Query**: Enter questions in natural language
3. **Memory**: Conversations are tracked by session ID
4. **Response**: Receive validated JSON with:
   - Answer based on documents
   - Confidence level
   - Source citations
5. **Exit**: Type `exit` or `quit` to terminate

### API Usage

1. **Initialize**: API loads vector store on startup
2. **Authenticate**: Include API key in `X-API-Key` header
3. **Query**: POST to `/query` endpoint with JSON payload
4. **Stream**: POST to `/query/stream` for real-time responses
5. **Memory**: Use consistent `session_id` for multi-turn conversations
6. **Upload**: POST documents to `/documents/upload` endpoint

## 📊 Example Output

### Standard Response

```json
{
  "answer": "Guardrails AI ensures LLMs follow strict validation rules by validating outputs against predefined schemas.",
  "confidence": "high",
  "sources": ["sample.txt"]
}
```

### Streaming Response

```text
Guardrails AI ensures LLMs follow strict validation...
[tokens streamed in real-time]
```

## ✨ Key Features

### 🛡️ Advanced Security & Validation

- **Input Validation**: Query length and format checks
- **Output Validation**: Schema compliance via Guardrails
- **Toxicity Detection**: Filters harmful content
- **PII Detection**: Removes sensitive information (email, phone, SSN)
- **API Authentication**: Secure endpoints with API keys
- **Source Citation**: Tracks which documents informed each answer
- **Confidence Scoring**: Reliability indicators
- **Refusal Handling**: Structured refusals when information is unavailable

### 💬 Conversation Memory

- **Redis Backend**: Production-grade storage
- **In-Memory Fallback**: Works without Redis
- **Session Tracking**: Multi-turn conversations
- **TTL Management**: Auto-cleanup after 1 hour
- **Context Retention**: Maintains conversation history

### 🌊 Streaming Responses

- **Real-time**: Tokens streamed as generated
- **Async Support**: Non-blocking operations
- **Better UX**: Progressive display for long responses
- **Memory Integration**: Saves complete response after streaming

### 📝 Structured Logging

- **Production-Ready**: Contextual structured logs
- **ISO Timestamps**: Precise timing information
- **Log Levels**: Configurable verbosity
- **Error Tracking**: Comprehensive error logging
- **Performance Monitoring**: Query timing and metrics

### 📄 Document Management

- **Multiple Formats**: .txt, .pdf support
- **Metadata Tracking**: Filename, size, date, extension
- **Metadata Filtering**: Query by document properties
- **Upload API**: Runtime document additions
- **Auto-Indexing**: Vector store updates on upload

### 🧪 Testing & Quality

- **Unit Tests**: Comprehensive test coverage
- **Integration Tests**: API endpoint testing
- **Pytest**: Industry-standard testing framework
- **Code Coverage**: Track test effectiveness

## 🧪 Customization

### Change the LLM Model

Edit `.env`:

```bash
MODEL_NAME=gpt-3.5-turbo  # or gpt-4, etc.
TEMPERATURE=0.7
```

### Adjust RAG Settings

Edit `.env`:

```bash
K_RETRIEVAL=5  # Retrieve more documents
CHUNK_SIZE=500  # Smaller chunks
CHUNK_OVERLAP=100
```

### Configure Redis Memory

Edit `.env`:

```bash
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

### Add Custom Guardrails

Edit `schemas.py`:

```python
from guardrails.hub import ToxicLanguage, DetectPII, RegexMatch

answer: str = Field(
    validators=[
        ValidLength(min=5, max=1000, on_fail="fix"),
        ToxicLanguage(threshold=0.5, on_fail="exception"),
        DetectPII(pii_entities=["EMAIL_ADDRESS", "PHONE_NUMBER"], on_fail="fix"),
        RegexMatch(regex=r"^[A-Za-z0-9\s.,!?-]+$", on_fail="reask")
    ]
)
```

### Enable/Disable Features

Edit `.env`:

```bash
ENABLE_TOXICITY_CHECK=true
ENABLE_PII_DETECTION=true
LOG_LEVEL=INFO
API_KEY=your-secure-api-key
```

### Document Metadata Filtering

Use programmatically:

```python
from ingestion import KnowledgeBase

kb = KnowledgeBase()

# Filter by extension
pdf_docs = kb.load_documents(filter_metadata={"extension": ".pdf"})

# Filter by any metadata field
recent_docs = kb.load_documents(filter_metadata={"author": "John Doe"})
```

## 🧪 Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run with Coverage

```bash
pytest tests/ --cov=. --cov-report=html
```

### Run Specific Tests

```bash
pytest tests/test_api.py -v
pytest tests/test_schemas.py::test_rag_response_valid -v
```

## 🐳 Optional: Redis Setup

### Using Docker

```bash
docker run -d -p 6379:6379 redis:latest
```

### Using Homebrew (macOS)

```bash
brew install redis
brew services start redis
```

### Verify Redis Connection

```bash
redis-cli ping
# Should return: PONG
```

## 📊 Monitoring & Logs

### View Logs

```bash
tail -f app.log
```

### Configure Logging

Edit `.env`:

```bash
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR
LOG_FILE=app.log
```

### Structured Log Output

```json
{
  "event": "Query completed successfully",
  "timestamp": "2025-12-24T10:30:45.123Z",
  "level": "info",
  "confidence": "high",
  "sources_count": 2,
  "session_id": "user123"
}
```

## 📝 Notes

- Vector store is cached in `faiss_index/` directory
- Set `force_rebuild=True` when adding new documents (CLI mode)
- Use `/documents/upload` endpoint for runtime document additions (API mode)
- Requires active OpenAI API key with sufficient credits
- Redis is optional - system falls back to in-memory storage
- API documentation available at `/docs` when server is running
- All sensitive data (API keys, .env) is excluded via `.gitignore`
- Conversation memory expires after 1 hour (configurable)
- Supports both synchronous and streaming responses

## 🚀 Production Deployment

### Environment Variables

```bash
OPENAI_API_KEY=sk-prod-key
API_KEY=secure-random-string-here
ALLOWED_ORIGINS=https://yourdomain.com
LOG_LEVEL=WARNING
REDIS_HOST=redis-server
```

### Docker Deployment

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t securerag .
docker run -p 8000:8000 --env-file .env securerag
```

### Docker Compose

```yaml
version: "3.8"
services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - redis

  redis:
    image: redis:latest
    ports:
      - "6379:6379"
```

## 🔍 Troubleshooting

### Issue: "OPENAI_API_KEY not found"

**Solution**: Ensure `.env` file exists with `OPENAI_API_KEY=sk-...`

### Issue: Redis connection failed

**Solution**: System automatically falls back to in-memory storage. Install Redis or disable memory features.

### Issue: No documents found

**Solution**: Place .txt or .pdf files in `./documents/` directory. System creates a sample document automatically.

### Issue: Import errors

**Solution**:

```bash
pip install -r requirements.txt
```

### Issue: API authentication failed

**Solution**: Include API key in header: `-H "X-API-Key: your-key"`

### Issue: Guardrails validation errors

**Solution**: Check logs for specific validation failures. Adjust validators in `schemas.py` if needed.

## 📚 Documentation

- **Setup Guide**: See [SETUP.md](SETUP.md) for detailed setup instructions
- **API Documentation**: Available at http://localhost:8000/docs when running
- **Enhancements**: See [ENHANCEMENTS.md](ENHANCEMENTS.md) for feature details

## 🛠️ Technology Stack

- **LangChain**: RAG orchestration and document processing
- **Guardrails AI**: Output validation and safety
- **FastAPI**: Modern web framework for APIs
- **OpenAI**: GPT models for generation
- **FAISS**: Vector similarity search
- **Redis**: Conversation memory backend
- **Pydantic**: Data validation
- **Structlog**: Structured logging
- **Pytest**: Testing framework

## 🤝 Contributing

Feel free to submit issues or pull requests to improve SecureRAG!

## 📄 License

MIT License - feel free to use this project for your own applications.

---

