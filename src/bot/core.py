"""Core bot functionality and initialization."""
import asyncio
import logging
from typing import Optional

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)

from src.config import Config

logger = logging.getLogger(__name__)


class TelegramBot:
    """Main Telegram bot class."""
    
    def __init__(self, config: Config):
        """Initialize the bot.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.application: Optional[Application] = None
        self.registry = None
        
    def set_registry(self, registry):
        """Set the feature registry.
        
        Args:
            registry: FeatureRegistry instance
        """
        self.registry = registry
        
    async def initialize(self):
        """Initialize the bot application."""
        logger.info("Initializing Telegram bot...")
        
        # Create application
        self.application = Application.builder().token(self.config.telegram_bot_token).build()
        
        # Register handlers
        self._register_handlers()
        
        logger.info("Bot initialized successfully")
    
    def _register_handlers(self):
        """Register all command and callback handlers."""
        if not self.application:
            raise RuntimeError("Application not initialized")
        
        # Register features from registry
        if self.registry:
            for feature in self.registry.get_all():
                # Register command handlers
                if hasattr(feature, 'handle_command'):
                    self.application.add_handler(
                        CommandHandler(feature.command, feature.handle_command)
                    )
                
                # Register callback handlers for inline buttons
                if hasattr(feature, 'handle_callback'):
                    self.application.add_handler(
                        CallbackQueryHandler(feature.handle_callback, pattern=feature.callback_pattern)
                    )
                
                # Register message handlers if feature has handle_message method
                if hasattr(feature, 'handle_message'):
                    self.application.add_handler(
                        MessageHandler(filters.TEXT & ~filters.COMMAND, feature.handle_message)
                    )
                
                logger.info(f"Registered handlers for feature: {feature.command}")
        
        logger.info("Handlers registered")
    
    async def start(self):
        """Start the bot."""
        if not self.application:
            await self.initialize()
        
        logger.info("Starting bot...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
    async def stop(self):
        """Stop the bot gracefully."""
        if self.application:
            logger.info("Stopping bot...")
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
    
    async def run(self):
        """Run the bot (blocking)."""
        try:
            await self.start()
            logger.info("Bot is running. Press Ctrl+C to stop.")
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        finally:
            await self.stop()

