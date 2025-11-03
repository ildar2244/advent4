"""DTO classes for OpenAI-compatible API."""
from pydantic import BaseModel
from typing import List


class OpenAIMessage(BaseModel):
    """OpenAI message model."""
    role: str
    content: str


class OpenAIRequest(BaseModel):
    """OpenAI request model for ProxyAPI."""
    model: str
    messages: List[OpenAIMessage]
    stream: bool = True


class OpenAIResponse(BaseModel):
    """OpenAI response model."""
    id: str
    choices: List[dict]
    model: str

