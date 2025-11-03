"""Chat feature implementation for Day 01 with multi-LLM support."""
import logging
from typing import AsyncGenerator

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src.features.base import BaseFeature
from src.llm.base import BaseLLM
from src.llm.factory import LLMFactory
from src.utils.typing import LLMResponse

logger = logging.getLogger(__name__)


class ChatFeature(BaseFeature):
    """Chat feature allowing users to chat with AI and select LLM provider."""
    
    def __init__(self, config):
        """Initialize chat feature.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.llm_providers = {}
        self._conversations = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize LLM providers."""
        for provider_name in LLMFactory.get_available_providers():
            try:
                provider = LLMFactory.create(provider_name, self.config)
                self.llm_providers[provider_name] = provider
                logger.info(f"Initialized provider: {provider_name}")
            except Exception as e:
                logger.error(f"Failed to initialize provider {provider_name}: {e}")
    
    @property
    def command(self) -> str:
        """Return the command name."""
        return "start"
    
    @property
    def callback_pattern(self) -> str:
        """Return the callback pattern for inline buttons."""
        return "^llm_"
    
    def get_model_selection_keyboard(self) -> InlineKeyboardMarkup:
        """Get inline keyboard for model selection."""
        keyboard = []
        for provider_name, provider in self.llm_providers.items():
            keyboard.append([
                InlineKeyboardButton(
                    provider.display_name,
                    callback_data=f"llm_{provider_name}"
                )
            ])
        return InlineKeyboardMarkup(keyboard)
    
    async def handle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        user_id = update.effective_user.id
        message = update.message
        
        if not message:
            return
        
        # Initialize user data
        if 'selected_llm' not in context.user_data:
            context.user_data['selected_llm'] = LLMFactory.get_default_provider()
        
        welcome_message = (
            "👋 Привет! Я твой ИИ-ассистент с поддержкой нескольких моделей!\n\n"
            "Выбери модель для начала диалога:"
        )
        
        keyboard = self.get_model_selection_keyboard()
        await message.reply_text(welcome_message, reply_markup=keyboard)
        
        # Show instructions
        instructions = (
            "📝 Как использовать:\n"
            "1. Выбери модель нажав на кнопку\n"
            "2. Просто напиши свой вопрос\n"
            "3. Бот ответит используя выбранную модель\n\n"
            "Используй кнопки выше чтобы переключить модель в любой момент"
        )
        await message.reply_text(instructions)
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback from model selection buttons."""
        query = update.callback_query
        
        if not query:
            return
        
        await query.answer()
        
        # Extract provider name from callback_data
        provider_name = query.data.replace("llm_", "")
        
        if provider_name not in self.llm_providers:
            await query.edit_message_text(
                f"❌ Ошибка: модель '{provider_name}' не найдена"
            )
            return
        
        # Save selected provider
        context.user_data['selected_llm'] = provider_name
        
        provider = self.llm_providers[provider_name]
        await query.edit_message_text(
            f"✅ Выбрана модель: {provider.display_name}\n\n"
            "Напиши свой вопрос!"
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages."""
        user_id = update.effective_user.id
        message = update.message
        
        if not message or not message.text:
            return
        
        # Get selected LLM provider
        provider_name = context.user_data.get('selected_llm', LLMFactory.get_default_provider())
        
        if provider_name not in self.llm_providers:
            await message.reply_text(
                "❌ Ошибка: модель не выбрана. Используй /start для выбора модели."
            )
            return
        
        provider = self.llm_providers[provider_name]
        
        # Get conversation history
        conversation_history = self._conversations.get(user_id, [])
        
        try:
            # Send typing indicator
            from src.bot.handlers.base import BaseHandler
            await BaseHandler.send_typing_indicator(context, update.effective_chat.id)
            
            # Generate response
            full_response = ""
            model_name = ""
            
            async for response_chunk in provider.generate_response(message.text):
                full_response += response_chunk.content
                model_name = response_chunk.model_name
            
            # Update conversation history
            conversation_history.append({"role": "user", "content": message.text})
            conversation_history.append({"role": "assistant", "content": full_response})
            self._conversations[user_id] = conversation_history
            
            # Send response with model info
            response_message = self._format_response(full_response, model_name)
            
            # Add keyboard for quick model switch
            keyboard = self.get_model_selection_keyboard()
            await message.reply_text(response_message, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"Error generating response: {e}", exc_info=True)
            error_message = (
                "❌ Произошла ошибка при генерации ответа.\n\n"
                "Пожалуйста, попробуйте позже или выберите другую модель."
            )
            await message.reply_text(error_message)
    
    @staticmethod
    def _format_response(content: str, model: str) -> str:
        """Format response with model information.
        
        Args:
            content: Response content
            model: Model name
            
        Returns:
            Formatted response
        """
        return f"{content}\n\n---\n🤖 Модель: {model}"

