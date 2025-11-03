"""Base handler for bot commands."""
import logging

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


class BaseHandler:
    """Base handler class."""
    
    @staticmethod
    async def send_typing_indicator(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
        """Send typing indicator to show bot is processing.
        
        Args:
            context: Update context
            chat_id: Chat ID
        """
        try:
            await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        except Exception as e:
            logger.warning(f"Failed to send typing indicator: {e}")

