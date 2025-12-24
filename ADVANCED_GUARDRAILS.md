# Advanced Guardrails Setup

The SecureRAG project uses Pydantic validation by default for compatibility. If you want to enable advanced Guardrails validators like toxicity detection and PII filtering, follow these steps:

## Installing Advanced Validators

**Note**: Advanced Guardrails validators are **optional**. The system works perfectly with basic Pydantic validators by default.

Guardrails validators require authentication and are installed separately from the Guardrails Hub:

### Step 1: Get a Guardrails Hub API Token

1. Visit https://hub.guardrailsai.com/keys
2. Sign up or log in to your account
3. Generate an API token

### Step 2: Configure Guardrails

```bash
# Configure guardrails with your token
guardrails configure

# You'll be prompted to enter your API token
```

### Step 3: Install Validators

```bash
# Install the Guardrails CLI if not already installed
pip install guardrails-ai

# Install specific validators
guardrails hub install hub://guardrails/toxic_language
guardrails hub install hub://guardrails/detect_pii
guardrails hub install hub://guardrails/valid_length
```

### Alternative: Skip Advanced Validators

If you don't want to set up Guardrails Hub authentication, the system works great with the default Pydantic validators already configured in `schemas.py`.

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

### Authentication Error (401 Unauthorized)

If you see:
```
ERROR:guardrails-cli:401
ERROR:guardrails-cli:Unauthorized
ERROR:guardrails-cli:Your token is invalid.
```

**Solution**:
1. Get a token from https://hub.guardrailsai.com/keys
2. Run `guardrails configure` and enter your token
3. Try installing validators again

**Alternative**: Continue using the default Pydantic validators (already working in the system).

### Import Error

If you see `ImportError: cannot import name 'ValidLength'`, the validator is not installed:

```bash
guardrails hub install hub://guardrails/valid_length
```

Note: This requires authentication (see above).

### Validation Failures

Check the Guardrails documentation for each validator's configuration options and adjust thresholds as needed.

### Performance

Advanced validators may add latency. Monitor performance and adjust as needed for production use.

### Why Advanced Validators Are Optional

The SecureRAG system is designed to work perfectly without advanced Guardrails validators:
- **Basic Pydantic validation** handles length, type checking, and structure validation
- **LLM prompting** already enforces appropriate content through system instructions
- **Advanced validators** are useful for additional safety layers in production but not required for core functionality

## Learn More

- [Guardrails Documentation](https://docs.guardrailsai.com/)
- [Guardrails Hub](https://hub.guardrailsai.com/)
- [Custom Validators](https://docs.guardrailsai.com/custom_validators/)
