# SecureRAG

Production-grade Retrieval-Augmented Generation (RAG) system with enterprise security and validation. Combines LangChain orchestration with Guardrails AI for reliable, structured, and compliant LLM outputs.

## Overview

SecureRAG implements advanced content safety, privacy protection, and quality control for RAG applications:

- **Content Safety**: Toxicity detection and filtering
- **Privacy Protection**: Automated PII detection and redaction
- **Quality Control**: Response length and format validation
- **Conversation Memory**: Redis-backed multi-turn conversations
- **REST API**: Full-featured FastAPI service
- **Source Attribution**: Document citations with confidence scoring
- **Structured Logging**: Production-ready observability

## Architecture

```
User Query → FastAPI/CLI → FAISS Vector Store → RAG Engine → LLM Generation →
Guardrails Validation (ToxicLanguage, DetectPII, ValidLength) → Structured Response
```

## Project Structure

### Core Files

### **`config.py`**

Enhanced configuration with environment variable support:

- **Model Settings**: GPT model selection and temperature
- **RAG Parameters**: Chunk size, overlap, and retrieval count (k)
- \*\*PathsComponents

**`config.py`** - Environment-based configuration management

**`schemas.py`** - Pydantic schemas with Guardrails validators:

- ToxicLanguage: Content safety validation
- DetectPII: Automated PII redaction (email, phone, SSN)
- ValidLength: Response length control (5-1000 characters)

**`ingestion.py`** - Document processing and FAISS vector store management

**`engine.py`** - RAG pipeline orchestration with conversation memory

**`main.py`** - Interactive CLI interface

**`api.py`** - FastAPI REST service

### API Endpoints

- `GET /health` - System health status
- `POST /query` - Query with conversation memory
- `POST /query/stream` - Streaming responses
- `POST /documents/upload` - Document upload
- `DELETE /documents/{filename}` - Document deletion
- `GET /documents` - List all documents
- `DELETE /memory/{session_id}` - Clear conversation historybash
  git clone https://github.com/abdull6771/SecureRAG.git
  cd SecureRAG

````

2. **Install dependencies:**

```bash
pip install -r requirements.txt
````

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

````Getting Started

### Installation

```bash
git clone https://github.com/abdull6771/SecureRAG.git
cd SecureRAG
pip install -r requirements.txt
````

### Configuration

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Guardrails Setup

```bash
guardrails configure --token <your-guardrails-token>
guardrails hub install hub://guardrails/toxic_language
guardrails hub install hub://guardrails/detect_pii
guardrails hub install hub://guardrails/valid_length
```

### Running

**CLI Interface:**

```bash
python main.py
```

**REST API:**

````bash
uvicorn api:app --host 127.0.0.1 --port 8000
# Documentation: http://localhost:8000/docs

## 🧪 Customization

### Change the LLM Model

Edit `.env`:

```bash
MODEL_NAME=gpt-3.5-turbo  # or gpt-4, etc.
TEMPERATURE=0.7
````

### Adjust RAG Settings

Edit `.env`:

````bash
K_RETRIEVAL=5  # Retrieve more documents
CHUNK_SIZE=500  # Smaller chunks
CHUNK_OVERLAP=100
```API Usage

### Query Example

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is machine learning?",
    "session_id": "user123"
  }'
````

### Response Format

````json
{
  "answer": "Machine learning is...",
  "confidence": "high",
  "sources": ["document.pdf"]
}

```bash
tail -f app.log
````

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

````yaml
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

  rKey Features

### Security & Validation

**ToxicLanguage Validator**
- Sentence-level toxicity analysis
- Blocks harmful, offensive content
- Configurable threshold (default: 0.5)
- Essential for customer-facing applications

**DetectPII Validator**
- Automated PII detection using Microsoft Presidio
- Redacts emails, phone numbers, SSNs
- GDPR/CCPA compliance by default
- Real-time privacy protection

**ValidLength Validator**
- Response length control (5-1000 characters)
- Auto-correction for violations
- Prevents LLM verbosity
- Ensures consistent quality

### Additional Features

- Conversation memory with Redis backend
- Streaming responses for real-time UX
- Structured logging with contextual information
- Document metadata tracking and filtering
- Source citation with confidence scoring
- **Pydantic**: Data validation
- **Structlog**: Structured logging
- **Pytest**: Testing framework

## 🤝 Contributing

Feel free to submit issues or pull requests to improve SecureRAG!

## 📄 License

MIT License - feel free to use this project for your own applications.

---

Configuration

### Environment Variables

```bash
# Model Settings
MODEL_NAME=gpt-4o
TEMPERATURE=0.0

# RAG Parameters
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
K_RETRIEVAL=3

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# Guardrails
ENABLE_TOXICITY_CHECK=true
ENABLE_PII_DETECTION=true
````
