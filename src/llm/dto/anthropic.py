"""DTO classes for Anthropic-compatible API."""
from pydantic import BaseModel
from typing import List


class AnthropicMessage(BaseModel):
    """Anthropic message model."""
    role: str
    content: str


class AnthropicRequest(BaseModel):
    """Anthropic request model for ProxyAPI."""
    model: str
    messages: List[AnthropicMessage]
    max_tokens: int = 1000
    stream: bool = True


class AnthropicResponse(BaseModel):
    """Anthropic response model."""
    id: str
    content: List[dict]
    model: str

