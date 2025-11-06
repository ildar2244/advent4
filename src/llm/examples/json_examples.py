"""Примеры использования JSON-ответов от LLM."""
import asyncio
import json
from typing import Dict, Any

from src.llm.factory import LLMFactory
from src.config import Config


async def example_json_response():
    """Пример использования JSON-ответов от LLM."""
    # Загрузка конфигурации
    config = Config.from_env()
    
    # Создание провайдера
    llm = LLMFactory.create("gpt", config)
    
    try:
        # Пример 1: Получение JSON-ответа
        print("=== Пример 1: JSON-ответ ===")
        prompt = "Какие основные принципы программирования вы знаете? Ответь в формате JSON."
        
        async for response in llm.generate_json_response(prompt):
            print(f"Ответ: {response.content}")
            
            # Парсинг JSON-ответа
            try:
                json_data = json.loads(response.content)
                print(f"Статус: {json_data.get('status')}")
                print(f"Данные: {json_data.get('data')}")
                print(f"Ошибка: {json_data.get('error')}")
            except json.JSONDecodeError as e:
                print(f"Ошибка парсинга JSON: {e}")
        
        # Пример 2: Использование обычного ответа с JSON-форматом
        print("\n=== Пример 2: Обычный ответ с JSON-форматом ===")
        prompt = "Опиши основные преимущества Python"
        
        async for response in llm.generate_response(prompt, json_format=True):
            print(f"Ответ: {response.content}")
            
            # Парсинг JSON-ответа
            try:
                json_data = json.loads(response.content)
                print(f"Статус: {json_data.get('status')}")
                if json_data.get('data'):
                    print(f"Содержимое: {json_data['data'].get('content')}")
            except json.JSONDecodeError as e:
                print(f"Ошибка парсинга JSON: {e}")
        
        # Пример 3: Обычный текстовый ответ
        print("\n=== Пример 3: Обычный текстовый ответ ===")
        prompt = "Кратко расскажи о Python"
        
        async for response in llm.generate_response(prompt, json_format=False):
            print(f"Ответ: {response.content}")
            
    finally:
        await llm.close()


async def example_custom_json_structure():
    """Пример использования кастомной JSON-структуры."""
    config = Config.from_env()
    llm = LLMFactory.create("claude", config)
    
    try:
        # Пример с кастомной структурой
        prompt = """
        Проанализируй следующий текст и верни ответ в формате JSON:
        {
            "analysis": {
                "sentiment": "positive|negative|neutral",
                "keywords": ["keyword1", "keyword2"],
                "summary": "Краткое резюме"
            },
            "confidence": 0.95
        }
        
        Текст для анализа: Python - это мощный и гибкий язык программирования с простым синтаксисом.
        """
        
        async for response in llm.generate_json_response(prompt):
            print(f"Анализ: {response.content}")
            
            # Парсинг кастомной структуры
            try:
                json_data = json.loads(response.content)
                analysis = json_data.get('data', {}).get('analysis', {})
                print(f"Тональность: {analysis.get('sentiment')}")
                print(f"Ключевые слова: {analysis.get('keywords')}")
                print(f"Уверенность: {json_data.get('data', {}).get('confidence')}")
            except json.JSONDecodeError as e:
                print(f"Ошибка парсинга JSON: {e}")
                
    finally:
        await llm.close()


if __name__ == "__main__":
    print("Запуск примеров использования JSON-ответов...")
    
    # Запуск примеров
    asyncio.run(example_json_response())
    asyncio.run(example_custom_json_structure())