"""Type definitions and dataclasses."""
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """Response from LLM provider."""
    content: str
    model_name: str
    provider_name: str

