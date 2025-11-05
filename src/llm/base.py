"""Base LLM interface and abstract classes."""
from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional

from src.utils.typing import LLMResponse
from src.llm.dto.json_response import JSONResponse


class BaseLLM(ABC):
    """Base class for all LLM providers."""
    
    def __init__(self, name: str, display_name: str):
        """Initialize LLM provider.
        
        Args:
            name: Internal name (e.g., 'gpt', 'claude')
            display_name: Display name (e.g., 'GPT-4o Mini')
        """
        self.name = name
        self.display_name = display_name
    
    @abstractmethod
    async def generate_response(self, prompt: str, json_format: bool = False) -> AsyncGenerator[LLMResponse, None]:
        """Generate response from LLM.
        
        Args:
            prompt: User's prompt/question
            json_format: Whether to require JSON format response
            
        Yields:
            LLMResponse: Streaming response chunks
        """
        pass
    
    @abstractmethod
    async def generate_json_response(self, prompt: str) -> AsyncGenerator[LLMResponse, None]:
        """Generate response in JSON format from LLM.
        
        Args:
            prompt: User's prompt/question
            
        Yields:
            LLMResponse: Streaming response chunks
        """
        pass
    
    @property
    def model_name(self) -> str:
        """Return the model name for display purposes.
        
        Returns:
            Display name of the model
        """
        return self.display_name
    
    @abstractmethod
    async def close(self):
        """Close the LLM connection and cleanup resources."""
        pass

