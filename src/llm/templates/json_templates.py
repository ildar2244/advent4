"""Шаблоны для JSON-ответов от LLM."""
import json
from typing import Dict, Any


def get_json_system_prompt() -> str:
    """Получить system prompt для требования JSON-формата ответа."""
    return """
Ты должен отвечать ТОЛЬКО в формате JSON. Не используй никаких других текстов, объяснений или форматирования.
Твой ответ должен быть валидным JSON, который можно сразу распарсить.

Пример правильного ответа:
{"status": "success", "data": {"content": "Твой ответ здесь"}, "error": null}

Пример ответа с ошибкой:
{"status": "error", "data": null, "error": "Описание ошибки"}

Пример JSON-формата для структурированных данных:
{
  "name": "John Doe",
  "age": 30,
  "isStudent": false,
  "courses": [
    "History",
    "Math"
  ],
  "address": {
    "street": "123 Main St",
    "city": "Anytown"
  }
}

Убедись, что JSON синтаксически корректен и содержит все необходимые поля.
"""


def get_json_response_template() -> Dict[str, Any]:
    """Получить шаблон JSON-ответа."""
    return {
        "status": "success",
        "data": None,
        "error": None
    }


def format_prompt_for_json_response(prompt: str) -> str:
    """Отформатировать промпт для получения JSON-ответа."""
    formatted_prompt = f"""
{get_json_system_prompt()}

Пользовательский запрос:
{prompt}

Ответ в формате JSON:
"""
    # Логируем полный system prompt для отладки
    import logging
    logger = logging.getLogger(__name__)
    logger.info("=== SYSTEM PROMPT FOR JSON FORMAT ===")
    logger.info("Full system prompt being sent to model:")
    logger.info("%s", formatted_prompt)
    logger.info("=== END SYSTEM PROMPT ===")
    
    return formatted_prompt


def validate_json_response(response_text: str) -> Dict[str, Any]:
    """Валидировать JSON-ответ от LLM."""
    try:
        response_data = json.loads(response_text)
        
        # Проверка обязательных полей
        required_fields = ["status", "data", "error"]
        for field in required_fields:
            if field not in response_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Проверка статуса
        if response_data["status"] not in ["success", "error"]:
            raise ValueError(f"Invalid status: {response_data['status']}")
        
        return response_data
    
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")
    except Exception as e:
        raise ValueError(f"Response validation error: {e}")