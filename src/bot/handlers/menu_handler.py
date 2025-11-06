"""Обработчик команды /menu для восстановления меню выбора модели."""
import logging
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler
from src.features.day_01.chat_feature import ChatFeature

logger = logging.getLogger(__name__)

async def handle_menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /menu."""
    message = update.message
    
    if not message:
        return
    
    # Получаем экземпляр ChatFeature из контекста приложения
    chat_feature = context.application.chat_feature
    
    # Создаем клавиатуру с кнопками выбора модели
    keyboard = chat_feature.get_model_keyboard()
    
    # Отправляем сообщение с клавиатурой
    await message.reply_text(
        "🔄 Меню восстановлено\n\n"
        "Выберите модель для общения:",
        reply_markup=keyboard
    )