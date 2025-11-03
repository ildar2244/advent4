"""Base feature interface."""
from abc import ABC, abstractmethod

from telegram import Update
from telegram.ext import ContextTypes


class BaseFeature(ABC):
    """Base class for all bot features."""
    
    @property
    @abstractmethod
    def command(self) -> str:
        """Return the command that activates this feature.
        
        Returns:
            Command name (e.g., "chat")
        """
        pass
    
    @property
    @abstractmethod
    def callback_pattern(self) -> str:
        """Return the callback pattern for inline buttons.
        
        Returns:
            Pattern for matching callbacks (e.g., "^llm_")
        """
        pass
    
    @abstractmethod
    async def handle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the feature command.
        
        Args:
            update: Telegram update object
            context: Update context
        """
        pass
    
    @abstractmethod
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback from inline buttons.
        
        Args:
            update: Telegram update object
            context: Update context
        """
        pass

