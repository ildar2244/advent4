"""Менеджер состояния для управления форматом ответа."""
import logging
from enum import Enum
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class ResponseFormat(Enum):
    """Типы форматов ответа."""
    TEXT = "text"
    JSON = "json"


class StateManager:
    """Менеджер состояния для управления форматом ответа."""
    
    def __init__(self):
        """Инициализация менеджера состояния."""
        self._user_states: Dict[int, Dict[str, ResponseFormat]] = {}
    
    def get_user_format(self, user_id: int) -> ResponseFormat:
        """Получить текущий формат ответа для пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Текущий формат ответа
        """
        return self._user_states.get(user_id, {}).get('response_format', ResponseFormat.TEXT)
    
    def set_user_format(self, user_id: int, format_type: ResponseFormat):
        """Установить формат ответа для пользователя.
        
        Args:
            user_id: ID пользователя
            format_type: Тип формата ответа
        """
        if user_id not in self._user_states:
            self._user_states[user_id] = {}
        
        self._user_states[user_id]['response_format'] = format_type
        logger.info(f"User {user_id} format set to {format_type.value}")
    
    def get_format_keyboard(self) -> list:
        """Получить клавиатуру для выбора формата ответа.
        
        Returns:
            Список кнопок для выбора формата
        """
        return [
            [
                {"text": "📄 Текстовый формат", "callback_data": "format_text"},
                {"text": "📋 JSON-формат", "callback_data": "format_json"}
            ]
        ]
    
    def get_format_status_text(self, user_id: int) -> str:
        """Получить текст с текущим статусом формата.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Текст с текущим статусом
        """
        current_format = self.get_user_format(user_id)
        format_emoji = "📄" if current_format == ResponseFormat.TEXT else "📋"
        format_name = "Текстовый формат" if current_format == ResponseFormat.TEXT else "JSON-формат"
        
        return f"{format_emoji} Текущий формат: {format_name}\n\nИспользуй /без формата или /json-формат для изменения"


# Глобальный экземпляр менеджера состояния
state_manager = StateManager()