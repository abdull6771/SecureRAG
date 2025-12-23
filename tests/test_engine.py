"""
Tests for the SecureRAG engine.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine import ConversationMemory

def test_conversation_memory_in_memory():
    """Test in-memory conversation storage (when Redis is unavailable)."""
    memory = ConversationMemory()
    
    session_id = "test-session"
    memory.add_message(session_id, "user", "Hello")
    memory.add_message(session_id, "assistant", "Hi there!")
    
    history = memory.get_history(session_id)
    
    assert len(history) >= 2
    assert history[-2]["role"] == "user"
    assert history[-1]["role"] == "assistant"

def test_conversation_memory_clear():
    """Test clearing conversation history."""
    memory = ConversationMemory()
    
    session_id = "test-session-clear"
    memory.add_message(session_id, "user", "Test message")
    
    history_before = memory.get_history(session_id)
    assert len(history_before) > 0
    
    memory.clear_history(session_id)
    history_after = memory.get_history(session_id)
    
    # Should be empty after clearing
    assert len(history_after) == 0

def test_conversation_memory_limit():
    """Test conversation history limit."""
    memory = ConversationMemory()
    
    session_id = "test-session-limit"
    
    # Add 15 messages
    for i in range(15):
        memory.add_message(session_id, "user", f"Message {i}")
    
    # Get last 5
    history = memory.get_history(session_id, limit=5)
    
    assert len(history) == 5
    assert history[0]["content"] == "Message 10"
    assert history[-1]["content"] == "Message 14"
