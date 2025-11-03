"""Tests for configuration module."""
import os
import pytest
from unittest.mock import patch

from src.config import Config


def test_config_from_env():
    """Test creating config from environment."""
    with patch.dict(os.environ, {
        'TELEGRAM_BOT_TOKEN': 'test_token',
        'PROXYAPI_API_KEY': 'test_key',
        'OPENAI_MODEL': 'gpt-4o-mini',
        'ANTHROPIC_MODEL': 'claude-test'
    }):
        config = Config.from_env()
        
        assert config.telegram_bot_token == 'test_token'
        assert config.proxyapi_api_key == 'test_key'
        assert config.openai_model == 'gpt-4o-mini'
        assert config.anthropic_model == 'claude-test'


def test_config_default_values():
    """Test default values when not specified."""
    with patch.dict(os.environ, {
        'TELEGRAM_BOT_TOKEN': 'test_token',
        'PROXYAPI_API_KEY': 'test_key'
    }, clear=True):
        config = Config.from_env()
        
        assert config.openai_model == 'gpt-4o-mini'
        assert config.openai_display_name == 'GPT-4o Mini'
        assert config.anthropic_model == 'claude-3-5-haiku-20241022'
        assert config.anthropic_display_name == 'Claude 3.5 Haiku'


def test_config_missing_token():
    """Test error when Telegram token is missing."""
    with patch.dict(os.environ, {'PROXYAPI_API_KEY': 'test_key'}, clear=True):
        with pytest.raises(ValueError, match="TELEGRAM_BOT_TOKEN"):
            Config.from_env()


def test_config_missing_proxyapi_key():
    """Test error when ProxyAPI key is missing."""
    with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'test_token'}, clear=True):
        with pytest.raises(ValueError, match="PROXYAPI_API_KEY"):
            Config.from_env()

