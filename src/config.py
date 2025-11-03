"""Application configuration."""
import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class Config:
    """Application configuration."""
    
    # Telegram
    telegram_bot_token: str
    
    # ProxyAPI
    proxyapi_api_key: str
    
    # OpenAI settings
    openai_proxy_url: str
    openai_model: str
    openai_display_name: str
    
    # Anthropic settings
    anthropic_proxy_url: str
    anthropic_model: str
    anthropic_display_name: str
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create config from environment variables.
        
        Returns:
            Config instance
            
        Raises:
            ValueError: If required environment variables are missing
        """
        # Required variables
        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not telegram_token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
        
        proxyapi_key = os.getenv("PROXYAPI_API_KEY")
        if not proxyapi_key:
            raise ValueError("PROXYAPI_API_KEY environment variable is required")
        
        # OpenAI settings
        openai_url = os.getenv("OPENAI_PROXY_URL", "https://api.proxyapi.ru/openai/v1/chat/completions")
        openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        openai_display = os.getenv("OPENAI_DISPLAY_NAME", "GPT-4o Mini")
        
        # Anthropic settings
        anthropic_url = os.getenv("ANTHROPIC_PROXY_URL", "https://api.proxyapi.ru/anthropic/v1/messages")
        anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-20241022")
        anthropic_display = os.getenv("ANTHROPIC_DISPLAY_NAME", "Claude 3.5 Haiku")
        
        return cls(
            telegram_bot_token=telegram_token,
            proxyapi_api_key=proxyapi_key,
            openai_proxy_url=openai_url,
            openai_model=openai_model,
            openai_display_name=openai_display,
            anthropic_proxy_url=anthropic_url,
            anthropic_model=anthropic_model,
            anthropic_display_name=anthropic_display
        )

