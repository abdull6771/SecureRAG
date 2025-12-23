"""
Unit tests for SecureRAG system.
Run with: pytest tests/
"""

import pytest
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import AppConfig

def test_config_defaults():
    """Test configuration defaults."""
    config = AppConfig()
    assert config.MODEL_NAME == os.getenv("MODEL_NAME", "gpt-4o")
    assert config.CHUNK_SIZE == int(os.getenv("CHUNK_SIZE", "1000"))
    assert config.K_RETRIEVAL == int(os.getenv("K_RETRIEVAL", "3"))

def test_config_paths():
    """Test configuration paths."""
    config = AppConfig()
    assert config.VECTOR_STORE_PATH is not None
    assert config.DOCS_PATH is not None
