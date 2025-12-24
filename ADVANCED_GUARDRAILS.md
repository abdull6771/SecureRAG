# Advanced Guardrails Setup

The SecureRAG project uses Pydantic validation by default for compatibility. If you want to enable advanced Guardrails validators like toxicity detection and PII filtering, follow these steps:

## Installing Advanced Validators

Guardrails validators are installed separately from the Guardrails Hub:

```bash
# Install the Guardrails CLI if not already installed
pip install guardrails-ai

# Install specific validators
guardrails hub install hub://guardrails/toxic_language
guardrails hub install hub://guardrails/detect_pii
guardrails hub install hub://guardrails/valid_length
```

## Available Validators

Visit the [Guardrails Hub](https://hub.guardrailsai.com/) to browse available validators:

- **toxic_language**: Detect and filter toxic/harmful content
- **detect_pii**: Remove personally identifiable information (email, phone, SSN)
- **valid_length**: Ensure text length within bounds
- **competitor_check**: Detect competitor mentions
- **profanity_free**: Filter profanity
- **sql_injection**: Detect SQL injection attempts
- And many more...

## Enabling in schemas.py

Once installed, update `schemas.py`:

```python
from typing import List, Literal
from pydantic import BaseModel, Field, validator
from guardrails.hub import ValidLength, ToxicLanguage, DetectPII

class RAGResponse(BaseModel):
    """Enhanced RAG response with advanced guardrails."""

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
        """Additional validation."""
        if not v or len(v.strip()) < 5:
            raise ValueError("Answer must be at least 5 characters long")
        return v.strip()
```

## Configuration

Update `.env` to enable/disable validators:

```bash
ENABLE_TOXICITY_CHECK=true
ENABLE_PII_DETECTION=true
MAX_RETRIES=3
```

## Current Status

**Default Configuration**: Uses basic Pydantic validators (length, type checking) for maximum compatibility.

**With Advanced Validators**: Requires manual installation of specific validators from Guardrails Hub.

## Benefits of Advanced Validators

- **Toxicity Detection**: Automatically filter harmful or offensive content
- **PII Protection**: Remove sensitive personal information from responses
- **Custom Validation**: Create domain-specific validation rules
- **Auto-Correction**: Automatically fix validation failures
- **Compliance**: Ensure outputs meet regulatory requirements

## Troubleshooting

### Import Error

If you see `ImportError: cannot import name 'ValidLength'`, the validator is not installed:

```bash
guardrails hub install hub://guardrails/valid_length
```

### Validation Failures

Check the Guardrails documentation for each validator's configuration options and adjust thresholds as needed.

### Performance

Advanced validators may add latency. Monitor performance and adjust as needed for production use.

## Learn More

- [Guardrails Documentation](https://docs.guardrailsai.com/)
- [Guardrails Hub](https://hub.guardrailsai.com/)
- [Custom Validators](https://docs.guardrailsai.com/custom_validators/)
