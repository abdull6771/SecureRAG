from typing import List, Literal
from pydantic import BaseModel, Field, validator
from guardrails.hub import ValidLength, ToxicLanguage, DetectPII

class RAGResponse(BaseModel):
    """
    Structured output schema for the RAG pipeline with advanced Guardrails validators.
    The LLM is forced to adhere to this structure with toxicity and PII detection.
    """
    
    answer: str = Field(
        description="The answer to the user's question based ONLY on the context.",
        validators=[
            ValidLength(min=5, max=1000, on_fail="fix"),
            ToxicLanguage(threshold=0.5, validation_method="sentence", on_fail="exception"),
            DetectPII(pii_entities=["EMAIL_ADDRESS", "PHONE_NUMBER", "SSN"], on_fail="fix")
        ]
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