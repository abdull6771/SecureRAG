"""
Tests for schemas and validation.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from schemas import RAGResponse, QueryRequest, DocumentUploadResponse
from pydantic import ValidationError

def test_rag_response_valid():
    """Test valid RAG response creation."""
    response = RAGResponse(
        answer="This is a valid answer.",
        confidence="high",
        sources=["doc1.txt", "doc2.pdf"]
    )
    
    assert response.answer == "This is a valid answer."
    assert response.confidence == "high"
    assert len(response.sources) == 2

def test_rag_response_invalid_confidence():
    """Test RAG response with invalid confidence level."""
    with pytest.raises(ValidationError):
        RAGResponse(
            answer="This is an answer.",
            confidence="invalid",  # Should be high/medium/low
            sources=[]
        )

def test_query_request_valid():
    """Test valid query request."""
    request = QueryRequest(
        query="What is machine learning?",
        session_id="test-session",
        stream=False
    )
    
    assert request.query == "What is machine learning?"
    assert request.session_id == "test-session"
    assert request.stream is False

def test_query_request_too_short():
    """Test query request with too short query."""
    with pytest.raises(ValidationError):
        QueryRequest(query="Hi")  # Less than 3 characters

def test_query_request_too_long():
    """Test query request with too long query."""
    with pytest.raises(ValidationError):
        QueryRequest(query="x" * 501)  # More than 500 characters

def test_document_upload_response():
    """Test document upload response."""
    response = DocumentUploadResponse(
        filename="test.pdf",
        status="success",
        message="Document uploaded successfully",
        document_count=1
    )
    
    assert response.filename == "test.pdf"
    assert response.status == "success"
    assert response.document_count == 1
