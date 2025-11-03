"""Main entry point for the bot."""
import asyncio
import logging
import sys

from src.bot.core import TelegramBot
from src.config import Config
from src.features.registry import FeatureRegistry
from src.features.day_01.chat_feature import ChatFeature

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main application entry point."""
    try:
        # Load configuration
        config = Config.from_env()
        logger.info("Configuration loaded successfully")
        
        # Initialize bot
        bot = TelegramBot(config)
        
        # Register features
        registry = FeatureRegistry()
        
        # Register Day 01 chat feature
        chat_feature = ChatFeature(config)
        registry.register(chat_feature)
        logger.info("Features registered")
        
        # Set registry in bot
        bot.set_registry(registry)
        
        # Initialize bot
        await bot.initialize()
        
        # Start bot
        logger.info("Starting bot...")
        await bot.start()
        
        # Keep bot running
        logger.info("Bot is running. Press Ctrl+C to stop.")
        await asyncio.Event().wait()
        
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        if 'bot' in locals():
            await bot.stop()
        if 'chat_feature' in locals():
            # Close all LLM providers
            for provider in chat_feature.llm_providers.values():
                await provider.close()
        logger.info("Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())
