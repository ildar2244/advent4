"""Factory for creating LLM instances."""
import logging
from typing import Dict, List, Optional, Type

from src.config import Config
from src.llm.base import BaseLLM
from src.llm.providers.openai_gpt import OpenAIGPTProvider
from src.llm.providers.anthropic_claude import AnthropicClaudeProvider

logger = logging.getLogger(__name__)


class LLMFactory:
    """Factory for creating LLM provider instances."""
    
    _providers: Dict[str, Type[BaseLLM]] = {
        "gpt": OpenAIGPTProvider,
        "claude": AnthropicClaudeProvider,
    }
    
    @classmethod
    def create(cls, provider_name: str, config: Config) -> BaseLLM:
        """Create an LLM instance.
        
        Args:
            provider_name: Name of the LLM provider (e.g., "gpt", "claude")
            config: Application configuration
            
        Returns:
            LLM instance
            
        Raises:
            ValueError: If provider is not supported
        """
        provider_name_lower = provider_name.lower()
        
        if provider_name_lower not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValueError(
                f"Unsupported LLM provider: {provider_name}. "
                f"Available providers: {available}"
            )
        
        provider_class = cls._providers[provider_name_lower]
        logger.info(f"Creating LLM instance: {provider_name_lower}")
        
        if provider_name_lower == "gpt":
            return provider_class(
                api_key=config.proxyapi_api_key,
                proxy_url=config.openai_proxy_url,
                model=config.openai_model,
                display_name=config.openai_display_name
            )
        elif provider_name_lower == "claude":
            return provider_class(
                api_key=config.proxyapi_api_key,
                proxy_url=config.anthropic_proxy_url,
                model=config.anthropic_model,
                display_name=config.anthropic_display_name
            )
    
    @classmethod
    def get_default_provider(cls) -> str:
        """Get the default LLM provider.
        
        Returns:
            Name of default provider
        """
        return "gpt"
    
    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get list of available LLM providers.
        
        Returns:
            List of provider names
        """
        return list(cls._providers.keys())
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[BaseLLM]):
        """Register a new LLM provider.
        
        Args:
            name: Provider name
            provider_class: Provider class
        """
        cls._providers[name.lower()] = provider_class
        logger.info(f"Registered new LLM provider: {name}")

