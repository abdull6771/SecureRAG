from typing import List, Literal
from pydantic import BaseModel, Field, validator

class RAGResponse(BaseModel):
    """
    Structured output schema for the RAG pipeline.
    The LLM is forced to adhere to this structure.
    """
    
    answer: str = Field(
        description="The answer to the user's question based ONLY on the context.",
        min_length=5,
        max_length=1000
    )
    confidence: Literal["high", "medium", "low"] = Field(
        description="Confidence level in the answer based on available context."
    )
    sources: List[str] = Field(
        description="List of filenames or document sources used to generate the answer."
    )

    @validator('answer')
    def validate_answer(cls, v):
        """Validate and clean the answer."""
        if not v or len(v.strip()) < 5:
            raise ValueError("Answer must be at least 5 characters long")
        return v.strip()

class QueryRequest(BaseModel):
    """Request schema for API queries."""
    query: str = Field(..., min_length=3, max_length=500, description="User question")
    session_id: str = Field(default=None, description="Session ID for conversation tracking")
    stream: bool = Field(default=False, description="Enable streaming response")

class DocumentUploadResponse(BaseModel):
    """Response schema for document upload."""
    filename: str
    status: str
    message: str
    document_count: int = Field(default=1)