"""Pytest configuration and fixtures."""
import pytest
from unittest.mock import AsyncMock, MagicMock

from src.config import Config


@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    return Config(
        telegram_bot_token="test_token",
        proxyapi_api_key="test_api_key",
        openai_proxy_url="https://test.openai.url",
        openai_model="gpt-4o-mini",
        openai_display_name="GPT-4o Mini",
        anthropic_proxy_url="https://test.anthropic.url",
        anthropic_model="claude-3-5-haiku-20241022",
        anthropic_display_name="Claude 3.5 Haiku"
    )


@pytest.fixture
def mock_update():
    """Create a mock Telegram update."""
    update = AsyncMock()
    update.effective_user.id = 12345
    update.effective_chat.id = 12345
    return update


@pytest.fixture
def mock_context():
    """Create a mock Telegram context."""
    context = AsyncMock()
    context.bot.send_chat_action = AsyncMock()
    context.user_data = {}
    return context

