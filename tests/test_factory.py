"""Tests for LLM factory."""
import pytest

from src.llm.factory import LLMFactory


def test_get_default_provider():
    """Test getting default provider."""
    default = LLMFactory.get_default_provider()
    assert default == "gpt"


def test_get_available_providers():
    """Test getting available providers."""
    providers = LLMFactory.get_available_providers()
    assert "gpt" in providers
    assert "claude" in providers


def test_create_unsupported_provider():
    """Test creating unsupported provider raises error."""
    from src.config import Config
    
    config = Config(
        telegram_bot_token="test",
        proxyapi_api_key="test",
        openai_proxy_url="https://test",
        openai_model="test",
        openai_display_name="Test",
        anthropic_proxy_url="https://test",
        anthropic_model="test",
        anthropic_display_name="Test"
    )
    
    with pytest.raises(ValueError, match="Unsupported LLM provider"):
        LLMFactory.create("unsupported", config)

