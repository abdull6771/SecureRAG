"""
Tests for the ingestion module.
"""

import pytest
import os
import sys
import tempfile
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ingestion import KnowledgeBase
from config import config

@pytest.fixture
def temp_docs_dir():
    """Create a temporary documents directory."""
    temp_dir = tempfile.mkdtemp()
    original_docs_path = config.DOCS_PATH
    config.DOCS_PATH = temp_dir
    
    # Create test documents
    with open(os.path.join(temp_dir, "test.txt"), "w") as f:
        f.write("This is a test document about machine learning.")
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)
    config.DOCS_PATH = original_docs_path

def test_knowledge_base_initialization():
    """Test KnowledgeBase initialization."""
    kb = KnowledgeBase()
    assert kb.embeddings is not None
    assert kb.vectorstore is None

def test_load_documents(temp_docs_dir):
    """Test document loading."""
    kb = KnowledgeBase()
    docs = kb.load_documents()
    
    assert len(docs) > 0
    assert all(hasattr(doc, 'page_content') for doc in docs)
    assert all(hasattr(doc, 'metadata') for doc in docs)

def test_load_documents_with_metadata_filter(temp_docs_dir):
    """Test document loading with metadata filtering."""
    kb = KnowledgeBase()
    
    # Load all documents
    all_docs = kb.load_documents()
    
    # Filter by extension
    filtered_docs = kb.load_documents(filter_metadata={"extension": ".txt"})
    
    assert len(filtered_docs) <= len(all_docs)
    assert all(doc.metadata.get("extension") == ".txt" for doc in filtered_docs)

def test_document_metadata_enhancement(temp_docs_dir):
    """Test that documents have enhanced metadata."""
    kb = KnowledgeBase()
    docs = kb.load_documents()
    
    for doc in docs:
        assert "filename" in doc.metadata
        assert "extension" in doc.metadata
        assert "upload_date" in doc.metadata
        assert "file_size" in doc.metadata
