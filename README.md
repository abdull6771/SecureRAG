# SecureRAG

**SecureRAG** is a production-grade Retrieval-Augmented Generation (RAG) system that combines **LangChain** for orchestration and **Guardrails AI** for structured output validation. This system ensures that LLM responses are always reliable, well-structured, and compliant with predefined schemas.

##  Project Overview

SecureRAG enables you to build question-answering systems that:

- Retrieve relevant information from your local document collection
- Generate accurate answers using OpenAI's GPT models
- Validate and structure responses using Guardrails AI
- Cite sources and provide confidence levels for transparency

##  Architecture

```
User Query → Knowledge Base (FAISS) → RAG Engine → LLM Generation → Guardrails Validation → Structured Response
```

##  Project Structure

### **`config.py`**

Central configuration file containing all system settings:

- **Model Settings**: GPT model selection and temperature
- **RAG Parameters**: Chunk size, overlap, and retrieval count (k)
- **Paths**: Vector store location and document directory
- **API Keys**: OpenAI API key management

**Key Configurations:**

```python
MODEL_NAME: "gpt-4o"
CHUNK_SIZE: 1000
CHUNK_OVERLAP: 200
K_RETRIEVAL: 3
```

### **`schemas.py`**

Defines the structured output schema using Pydantic and Guardrails:

- **RAGResponse**: Enforces structured JSON responses from the LLM
  - `answer`: The validated response (5-1000 characters)
  - `confidence`: Categorical confidence level (high/medium/low)
  - `sources`: List of document sources used
- Includes validators for answer length and quality control

### **`ingestion.py`**

Handles document loading and vector store creation:

- **KnowledgeBase Class**: Manages the document pipeline
  - Loads documents (.txt, .pdf) from the `./documents` directory
  - Splits documents into chunks using RecursiveCharacterTextSplitter
  - Creates FAISS vector embeddings using OpenAI embeddings
  - Saves/loads vector store for efficient reuse

**Features:**

- Auto-creates sample document if `./documents` is empty
- Supports force rebuild of vector store
- Error handling for document loading failures

### **`engine.py`**

Core RAG engine with Guardrails integration:

- **SecureRAGEngine Class**: Orchestrates the RAG pipeline
  - Initializes retriever, LLM, and Guardrails
  - Builds LCEL (LangChain Expression Language) chain
  - Formats retrieved documents with source citations
  - Validates LLM output against `RAGResponse` schema

**Pipeline Flow:**

1. Retrieve top-k relevant documents
2. Format documents with metadata
3. Generate response via GPT-4o
4. Parse and validate with Guardrails
5. Return structured JSON response

**Key Features:**

- Input validation (query length checks)
- System error fallback handling
- Automatic response repair if validation fails

### **`main.py`**

Application entry point with interactive CLI:

- Initializes Knowledge Base and RAG Engine
- Provides interactive query loop
- Displays structured responses in JSON format
- Supports `force_rebuild=True` for vector store updates

## 🚀Getting Started

### Prerequisites

```bash
pip install langchain langchain-openai langchain-community
pip install guardrails-ai faiss-cpu pypdf pydantic
```

### Setup

1. **Set your OpenAI API key:**

```bash
export OPENAI_API_KEY="sk-your-key-here"
```

2. **Add documents:**
   Place your .txt or .pdf files in the `./documents` directory.

3. **Run the system:**

```bash
python main.py
```

## 🔄 Usage Flow

1. **First Run**: Builds FAISS vector store from documents
2. **Query**: Enter questions in natural language
3. **Response**: Receive validated JSON with:
   - Answer based on documents
   - Confidence level
   - Source citations
4. **Exit**: Type `exit` or `quit` to terminate

## 📊 Example Output

```json
{
  "answer": "Guardrails AI ensures LLMs follow strict validation rules by validating outputs against predefined schemas.",
  "confidence": "high",
  "sources": ["sample.txt"]
}
```

## 🛡️ Security Features

- **Input Validation**: Rejects queries that are too short
- **Output Validation**: Enforces schema compliance via Guardrails
- **Source Citation**: Tracks which documents informed each answer
- **Confidence Scoring**: Indicates reliability of responses
- **Refusal Handling**: Returns structured refusals when information is unavailable

## 🧪 Customization

### Change the LLM Model

Edit `config.py`:

```python
MODEL_NAME: str = "gpt-3.5-turbo"  # or gpt-4, etc.
```

### Adjust Retrieval Settings

```python
K_RETRIEVAL: int = 5  # Retrieve more documents
CHUNK_SIZE: int = 500  # Smaller chunks
```

### Add Custom Validators

In `schemas.py`, add Guardrails validators:

```python
from guardrails.hub import ToxicLanguage

answer: str = Field(
    validators=[ValidLength(...), ToxicLanguage()]
)
```

## 📝 Notes

- Vector store is cached in `faiss_index/` directory
- Set `force_rebuild=True` in `main.py` when adding new documents
- Requires active OpenAI API key with sufficient credits

## 🤝 Contributing

Feel free to submit issues or pull requests to improve SecureRAG!

## 📄 License

MIT License - feel free to use this project for your own applications.

---

**Built with ❤️ using LangChain and Guardrails AI**
