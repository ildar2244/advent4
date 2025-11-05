"""Обработчики команд для управления форматом ответа."""
import logging

from telegram import Update
from telegram.ext import ContextTypes

from src.bot.state_manager import state_manager, ResponseFormat

logger = logging.getLogger(__name__)


async def handle_no_format_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /без формата."""
    user_id = update.effective_user.id
    message = update.message
    
    if not message:
        return
    
    # Установка текстового формата
    state_manager.set_user_format(user_id, ResponseFormat.TEXT)
    
    await message.reply_text(
        "✅ Установлен текстовый формат ответа.\n\n"
        "Все следующие ответы будут в обычном текстовом формате."
    )


async def handle_json_format_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /json-формат."""
    user_id = update.effective_user.id
    message = update.message
    
    if not message:
        return
    
    # Установка JSON формата
    state_manager.set_user_format(user_id, ResponseFormat.JSON)
    
    await message.reply_text(
        "✅ Установлен JSON-формат ответа.\n\n"
        "Все следующие ответы будут в формате JSON.\n\n"
        "Пример ответа:\n"
        "```json\n"
        "{\n"
        '  "status": "success",\n'
        '  "data": {\n'
        '    "content": "Текст ответа"\n'
        '  },\n'
        '  "error": null\n'
        "}\n"
        "```"
    )


async def handle_format_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик callback от кнопок выбора формата."""
    query = update.callback_query
    
    if not query:
        return
    
    await query.answer()
    
    user_id = query.from_user.id
    callback_data = query.data
    
    # Определение формата из callback_data
    if callback_data == "format_text":
        format_type = ResponseFormat.TEXT
        format_text = "📄 Текстовый формат"
    elif callback_data == "format_json":
        format_type = ResponseFormat.JSON
        format_text = "📋 JSON-формат"
    else:
        await query.edit_message_text("❌ Неизвестный формат")
        return
    
    # Установка формата
    state_manager.set_user_format(user_id, format_type)
    
    # Обновление сообщения
    await query.edit_message_text(
        f"✅ Выбран формат: {format_text}\n\n"
        "Все следующие ответы будут в выбранном формате."
    )