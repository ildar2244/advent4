"""Chat feature implementation for Day 01 with multi-LLM support."""
import logging
import json
from typing import AsyncGenerator

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src.features.base import BaseFeature
from src.llm.base import BaseLLM
from src.llm.factory import LLMFactory
from src.utils.typing import LLMResponse
from src.bot.state_manager import state_manager, ResponseFormat

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
    def commands(self) -> list[str]:
        """Return additional command names for format switching."""
        return ["json_format", "no_format"]
    
    @property
    def callback_pattern(self) -> str:
        """Return the callback pattern for inline buttons."""
        return "^(llm_|format_)"
    
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
    
    def get_model_keyboard(self) -> InlineKeyboardMarkup:
        """Get inline keyboard for model selection only."""
        keyboard = []
        for provider_name, provider in self.llm_providers.items():
            keyboard.append([
                InlineKeyboardButton(
                    provider.display_name,
                    callback_data=f"llm_{provider_name}"
                )
            ])
        return InlineKeyboardMarkup(keyboard)
    
    def get_combined_keyboard(self, user_id: int) -> InlineKeyboardMarkup:
        """Get combined keyboard with model selection and format control.
        
        Args:
            user_id: User ID for format detection
            
        Returns:
            Combined inline keyboard markup
        """
        keyboard = []
        
        # Add model selection buttons
        for provider_name, provider in self.llm_providers.items():
            keyboard.append([
                InlineKeyboardButton(
                    provider.display_name,
                    callback_data=f"llm_{provider_name}"
                )
            ])
        
        # Add separator
        keyboard.append([InlineKeyboardButton("⚙️ Формат ответа", callback_data="noop")])
        
        # Add format selection buttons
        current_format = state_manager.get_user_format(user_id)
        
        # Text format button
        text_button = InlineKeyboardButton(
            "📄 Текстовый" if current_format == ResponseFormat.JSON else "📄 Текстовый (выбран)",
            callback_data="format_text"
        )
        
        # JSON format button
        json_button = InlineKeyboardButton(
            "📋 JSON" if current_format == ResponseFormat.TEXT else "📋 JSON (выбран)",
            callback_data="format_json"
        )
        
        keyboard.append([text_button, json_button])
        
        return InlineKeyboardMarkup(keyboard)
    
    async def handle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start, /json_format, and /no_format commands."""
        user_id = update.effective_user.id
        message = update.message
        
        if not message:
            return
        
        command = message.text.replace('/', '').lower()
        
        # Handle format switching commands
        if command == "json_format":
            state_manager.set_user_format(user_id, ResponseFormat.JSON)
            await message.reply_text(
                "✅ Формат ответа изменен на: 📋 JSON-формат\n\n"
                "Теперь ответы будут генерироваться в JSON формате.\n"
                "Пример формата ответа будет передаваться в system prompt модели."
            )
            return
        
        elif command == "no_format":
            state_manager.set_user_format(user_id, ResponseFormat.TEXT)
            await message.reply_text(
                "✅ Формат ответа изменен на: 📄 Текстовый формат\n\n"
                "Теперь ответы будут генерироваться в текстовом формате."
            )
            return
        
        # Handle /start command
        # Initialize user data
        if 'selected_llm' not in context.user_data:
            context.user_data['selected_llm'] = LLMFactory.get_default_provider()
        
        # Get current format status
        current_format = state_manager.get_user_format(user_id)
        format_emoji = "📄" if current_format == ResponseFormat.TEXT else "📋"
        format_name = "Текстовый формат" if current_format == ResponseFormat.TEXT else "JSON-формат"
        
        welcome_message = (
            f"👋 Привет! Я твой ИИ-ассистент с поддержкой нескольких моделей!\n\n"
            f"Выбери модель для начала диалога:\n\n"
            f"{format_emoji} Текущий формат: {format_name}"
        )
        
        keyboard = self.get_model_keyboard()
        await message.reply_text(welcome_message, reply_markup=keyboard)
        
        # Show instructions
        instructions = (
            "📝 Как использовать:\n"
            "1. Выбери модель нажав на кнопку\n"
            "2. Просто напиши свой вопрос\n"
            "3. Бот ответит используя выбранную модель\n\n"
            "🔧 Управление моделями:\n"
            "• Используй /menu чтобы восстановить меню выбора модели\n"
            "• Используй /json_format для переключения в JSON формат\n"
            "• Используй /no_format для переключения в текстовый формат"
        )
        await message.reply_text(instructions)
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback from model selection and format control buttons."""
        query = update.callback_query
        
        if not query:
            return
        
        await query.answer()
        
        user_id = update.effective_user.id
        
        # Handle model selection callbacks
        if query.data.startswith("llm_"):
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
        
        # Handle format switching callbacks
        elif query.data.startswith("format_"):
            format_type = query.data.replace("format_", "")
            
            if format_type == "text":
                state_manager.set_user_format(user_id, ResponseFormat.TEXT)
                format_name = "Текстовый формат"
                format_emoji = "📄"
            elif format_type == "json":
                state_manager.set_user_format(user_id, ResponseFormat.JSON)
                format_name = "JSON-формат"
                format_emoji = "📋"
            else:
                await query.edit_message_text("❌ Неизвестный формат ответа")
                return
            
            await query.edit_message_text(
                f"✅ Формат ответа изменен на: {format_emoji} {format_name}\n\n"
                "Теперь ответы будут генерироваться в выбранном формате."
            )
        
        # Handle no-op callbacks (like separator buttons)
        elif query.data == "noop":
            # Just show the current state without changing anything
            current_format = state_manager.get_user_format(user_id)
            format_name = "Текстовый формат" if current_format == ResponseFormat.TEXT else "JSON-формат"
            format_emoji = "📄" if current_format == ResponseFormat.TEXT else "📋"
            
            await query.answer("Выберите формат ответа", show_alert=False)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages."""
        user_id = update.effective_user.id
        message = update.message
        
        if not message or not message.text:
            return
        
        # Check if message is a format command
        if message.text.startswith('/'):
            return  # Let command handlers process it
        
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
            
            # Get current response format
            response_format = state_manager.get_user_format(user_id)
            logger.info("=== CHAT FEATURE PROCESSING ===")
            logger.info("User ID: %s", user_id)
            logger.info("Selected LLM: %s", provider_name)
            logger.info("Response Format: %s", response_format)
            logger.info("User Prompt: %s", message.text)
            logger.info("=== END CHAT FEATURE INFO ===")
            
            # Generate response
            full_response = ""
            model_name = ""
            
            if response_format == ResponseFormat.JSON:
                # Generate JSON response (non-streaming)
                response_message = ""
                async for response_chunk in provider.generate_json_response(message.text):
                    response_message = response_chunk.content
                    model_name = response_chunk.model_name
                
                logger.info("=== JSON RESPONSE DEBUG ===")
                logger.info("Final response message: %s", response_message)
                logger.info("=== END JSON RESPONSE DEBUG ===")
            else:
                # Generate text response (non-streaming)
                response_message = ""
                async for response_chunk in provider.generate_response(message.text):
                    response_message = response_chunk.content
                    model_name = response_chunk.model_name
            
            # Send response without formatting to test for duplication
            logger.info("=== SENDING RESPONSE TO USER ===")
            logger.info("Raw response message: %s", response_message)
            logger.info("Response length: %s", len(response_message))
            logger.info("=== END SENDING RESPONSE ===")
            
            # Update conversation history with raw response
            conversation_history.append({"role": "user", "content": message.text})
            conversation_history.append({"role": "assistant", "content": response_message})
            self._conversations[user_id] = conversation_history
            
            # Add keyboard for model switch and format selection
            keyboard = self.get_combined_keyboard(user_id)
            
            # Send raw response without formatting
            await message.reply_text(response_message, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"Error generating response: {e}", exc_info=True)
            error_message = (
                "❌ Произошла ошибка при генерации ответа.\n\n"
                "Пожалуйста, попробуйте позже или выберите другую модель."
            )
            await message.reply_text(error_message)
    
    @staticmethod
    def _split_message(message: str, max_length: int = 4096) -> list[str]:
        """Split a long message into chunks that fit within Telegram's message limit.
        
        Args:
            message: The message to split
            max_length: Maximum length per chunk (default: 4096)
            
        Returns:
            List of message chunks
        """
        chunks = []
        
        # If message is short enough, return as single chunk
        if len(message) <= max_length:
            return [message]
        
        # Split by paragraphs first to maintain readability
        paragraphs = message.split('\n\n')
        current_chunk = ""
        
        for paragraph in paragraphs:
            # If adding this paragraph would exceed the limit, send current chunk and start new one
            if len(current_chunk) + len(paragraph) + 4 > max_length:  # +4 for newlines
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = paragraph
                else:
                    # Paragraph is too long by itself, split it further
                    if len(paragraph) > max_length:
                        # Split long paragraph by sentences or words
                        sentences = paragraph.split('. ')
                        for sentence in sentences:
                            if len(current_chunk) + len(sentence) + 2 > max_length:
                                if current_chunk:
                                    chunks.append(current_chunk)
                                    current_chunk = sentence
                                else:
                                    chunks.append(sentence)
                            else:
                                if current_chunk:
                                    current_chunk += ". " + sentence
                                else:
                                    current_chunk = sentence
                    else:
                        chunks.append(paragraph)
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
        
        # Add the last chunk if it's not empty
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    @staticmethod
    def _format_response(content: str, model: str, response_format: ResponseFormat = None) -> str:
        """Format response with model information.
        
        Args:
            content: Response content
            model: Model name
            response_format: Response format for special formatting
            
        Returns:
            Formatted response
        """
        if response_format == ResponseFormat.JSON:
            # Format JSON response as plain text with JSON prefix
            try:
                # Try to parse and reformat JSON for better readability
                json_data = json.loads(content)
                formatted_json = json.dumps(json_data, ensure_ascii=False, indent=2)
                return f"JSON-ответ:\n{formatted_json}\n\n🤖 Модель: {model}"
            except (json.JSONDecodeError, TypeError) as e:
                logger.warning(f"JSON formatting error: {e}")
                # If parsing fails, show as raw JSON
                return f"JSON-ответ:\n{content}\n\n🤖 Модель: {model}"
        else:
            # Regular text response
            return f"{content}\n\n🤖 Модель: {model}"

