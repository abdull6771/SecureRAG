from typing import List, Literal
from pydantic import BaseModel, Field, validator
from guardrails.hub import ValidLength

class RAGResponse(BaseModel):
    """
    Structured output schema for the RAG pipeline.
    The LLM is forced to adhere to this structure.
    """
    
    answer: str = Field(
        description="The answer to the user's question based ONLY on the context.",
        validators=[ValidLength(min=5, max=1000, on_fail="fix")]
    )
    confidence: Literal["high", "medium", "low"] = Field(
        description="Confidence level in the answer based on available context."
    )
    sources: List[str] = Field(
        description="List of filenames or document sources used to generate the answer."
    )

    @validator('answer')
    def validate_refusal(cls, v):
        """Standardize refusal messages if needed."""
        return v