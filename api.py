from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil

from ingestion import KnowledgeBase
from engine import SecureRAGEngine
from schemas import QueryRequest, RAGResponse, DocumentUploadResponse
from config import config, logger

# Initialize FastAPI
app = FastAPI(
    title="SecureRAG API",
    description="Production-grade RAG system with Guardrails AI",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
kb = None
rag_engine = None

@app.on_event("startup")
async def startup_event():
    """Initialize RAG system on startup."""
    global kb, rag_engine
    
    logger.info("Starting SecureRAG API", 
                host=config.API_HOST, 
                port=config.API_PORT)
    
    try:
        kb = KnowledgeBase()
        vectorstore = kb.get_vector_store(force_rebuild=False)
        rag_engine = SecureRAGEngine(vectorstore, enable_memory=True)
        logger.info("RAG engine initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize RAG engine", error=str(e))
        raise

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "SecureRAG",
        "version": "1.0.0",
        "model": config.MODEL_NAME,
        "vector_store": os.path.exists(config.VECTOR_STORE_PATH),
        "documents_path": os.path.exists(config.DOCS_PATH),
        "memory_enabled": rag_engine.memory is not None if rag_engine else False
    }

@app.post("/query", response_model=RAGResponse)
async def query_endpoint(request: QueryRequest):
    """Query the RAG system with optional conversation memory."""
    try:
        logger.info("Received query", 
                   query_preview=request.query[:50],
                   session_id=request.session_id)
        
        result = rag_engine.query(
            user_query=request.query,
            session_id=request.session_id
        )
        
        return result
    
    except Exception as e:
        logger.error("Query processing failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query/stream")
async def query_stream_endpoint(request: QueryRequest):
    """Stream the RAG response in real-time."""
    try:
        logger.info("Starting streaming query", 
                   query_preview=request.query[:50])
        
        async def generate():
            async for chunk in rag_engine.query_stream(
                user_query=request.query,
                session_id=request.session_id
            ):
                yield chunk
        
        return StreamingResponse(generate(), media_type="text/plain")
    
    except Exception as e:
        logger.error("Streaming query failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload a document to the knowledge base."""
    try:
        allowed_extensions = [".txt", ".pdf"]
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {allowed_extensions}"
            )
        
        file_path = os.path.join(config.DOCS_PATH, file.filename)
        os.makedirs(config.DOCS_PATH, exist_ok=True)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info("Document uploaded", filename=file.filename, size=file.size)
        
        vectorstore = kb.get_vector_store(force_rebuild=True)
        
        global rag_engine
        rag_engine = SecureRAGEngine(vectorstore, enable_memory=True)
        
        return DocumentUploadResponse(
            filename=file.filename,
            status="success",
            message="Document uploaded and indexed successfully",
            document_count=1
        )
    
    except Exception as e:
        logger.error("Document upload failed", error=str(e), filename=file.filename)
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents/{filename}")
async def delete_document(filename: str):
    """Delete a document from the knowledge base."""
    try:
        file_path = os.path.join(config.DOCS_PATH, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Document not found")
        
        os.remove(file_path)
        logger.info("Document deleted", filename=filename)
        
        vectorstore = kb.get_vector_store(force_rebuild=True)
        
        global rag_engine
        rag_engine = SecureRAGEngine(vectorstore, enable_memory=True)
        
        return {
            "status": "success",
            "message": f"Document {filename} deleted and vector store rebuilt"
        }
    
    except Exception as e:
        logger.error("Document deletion failed", error=str(e), filename=filename)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents")
async def list_documents():
    """List all documents in the knowledge base."""
    try:
        if not os.path.exists(config.DOCS_PATH):
            return {"documents": []}
        
        documents = []
        for filename in os.listdir(config.DOCS_PATH):
            file_path = os.path.join(config.DOCS_PATH, filename)
            if os.path.isfile(file_path):
                documents.append({
                    "filename": filename,
                    "size": os.path.getsize(file_path),
                    "extension": os.path.splitext(filename)[1]
                })
        
        return {"documents": documents, "count": len(documents)}
    
    except Exception as e:
        logger.error("Failed to list documents", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/memory/{session_id}")
async def clear_memory(session_id: str):
    """Clear conversation memory for a specific session."""
    try:
        if rag_engine.memory:
            rag_engine.memory.clear_history(session_id)
            logger.info("Memory cleared", session_id=session_id)
            return {
                "status": "success",
                "message": f"Conversation history cleared for session {session_id}"
            }
        else:
            raise HTTPException(status_code=400, detail="Memory not enabled")
    
    except Exception as e:
        logger.error("Failed to clear memory", error=str(e), session_id=session_id)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True,
        log_level=config.LOG_LEVEL.lower()
    )
