# JSON-ответы от LLM

## Описание

Модуль поддерживает получение ответов от LLM в формате JSON. Это позволяет легко парсить и обрабатывать ответы от моделей, структурировать данные и обеспечивать предсказуемый формат ответов.

## Функциональность

### 1. Поддержка JSON-формата

Все провайдеры (OpenAI GPT и Anthropic Claude) поддерживают два режима работы:
- **Текстовый режим** (по умолчанию) - обычные текстовые ответы
- **JSON-режим** - ответы в формате JSON

### 2. Структура JSON-ответа

Стандартная структура JSON-ответа:

```json
{
  "status": "success",
  "data": {
    "content": "Текст ответа от LLM"
  },
  "error": null
}
```

При ошибке:

```json
{
  "status": "error",
  "data": null,
  "error": "Описание ошибки"
}
```

## Использование

### 1. Получение JSON-ответа

```python
from src.llm.factory import LLMFactory
from src.config import Config

# Загрузка конфигурации
config = Config.from_env()
llm = LLMFactory.create("gpt", config)

try:
    # Получение JSON-ответа
    async for response in llm.generate_json_response("Какие основные принципы программирования вы знаете?"):
        print(f"Ответ: {response.content}")
        
        # Парсинг JSON
        import json
        json_data = json.loads(response.content)
        print(f"Статус: {json_data.get('status')}")
        print(f"Данные: {json_data.get('data')}")
        
finally:
    await llm.close()
```

### 2. Использование параметра в generate_response

```python
# Обычный текстовый ответ
async for response in llm.generate_response("Расскажи о Python", json_format=False):
    print(response.content)

# JSON-ответ
async for response in llm.generate_response("Расскажи о Python", json_format=True):
    print(response.content)
```

### 3. Кастомные JSON-структуры

Можно запрашивать кастомные структуры:

```python
prompt = """
Проанализируй текст и верни в формате JSON:
{
    "sentiment": "positive|negative|neutral",
    "keywords": ["keyword1", "keyword2"],
    "summary": "Краткое резюме"
}

Текст: Python - мощный язык программирования.
"""

async for response in llm.generate_json_response(prompt):
    json_data = json.loads(response.content)
    print(f"Тональность: {json_data['data']['sentiment']}")
```

## Компоненты

### 1. DTO для JSON-ответов

- [`JSONResponse`](src/llm/dto/json_response.py) - класс для работы с JSON-ответами
- Методы `success()` и `error()` для создания ответов

### 2. Шаблоны и валидация

- [`json_templates.py`](src/llm/templates/json_templates.py) - шаблоны для system prompt и валидация
- `get_json_system_prompt()` - system prompt для требования JSON-формата
- `validate_json_response()` - валидация JSON-ответов

### 3. Примеры использования

- [`json_examples.py`](src/llm/examples/json_examples.py) - примеры использования JSON-ответов

## Преимущества

1. **Структурированные ответы** - предсказуемый формат ответов
2. **Легкий парсинг** - ответы можно легко обрабатывать как JSON-объекты
3. **Обратная совместимость** - сохранение существующего функционала
4. **Гибкость** - поддержка разных форматов ответов
5. **Валидация** - автоматическая проверка JSON-структуры

## Обработка ошибок

Если LLM возвращает некорректный JSON, система:
- Логирует ошибку валидации
- Возвращает исходный ответ без изменений
- Продолжает работу без прерывания

## Совместимость

- OpenAI GPT (через ProxyAPI)
- Anthropic Claude (через ProxyAPI)
- Существующий код без изменений