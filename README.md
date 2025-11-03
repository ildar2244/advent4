# Advent4 - Telegram Bot with Multi-LLM Support via ProxyAPI

## Overview
A modular Telegram bot with multi-LLM integration via ProxyAPI, designed for daily feature expansion.

## Features
- 🤖 Basic Telegram bot with command handlers
- 💬 Multi-LLM support (GPT-4o Mini, Claude 3.5 Haiku) via ProxyAPI
- ⌨️ Inline buttons for model selection
- 📝 Model information in responses
- 🔧 Modular architecture for easy extension
- 🚀 Ready for additional LLM providers (YaGPT, GigaChat, etc.)

## Setup

### Prerequisites
- Python 3.9+
- Telegram Bot Token (get from @BotFather)
- ProxyAPI API Key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd advent4
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
cp .env.example .env
```

5. Configure environment variables in `.env`:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
PROXYAPI_API_KEY=your_proxyapi_api_key
```

6. Run the bot:
```bash
python src/main.py
```

## Usage

### Available Commands

- `/start` - Show main menu with model selection buttons

### Model Selection
After starting the bot, you'll see inline buttons to select your preferred LLM:
- GPT-4o Mini (default)
- Claude 3.5 Haiku

Simply click a button to switch models, or type your question to chat with the currently selected model.

### Example Interaction

```
User: /start
Bot: 👋 Привет! Я твой ИИ-ассистент с поддержкой нескольких моделей!
     [Inline buttons: GPT-4o Mini, Claude 3.5 Haiku]

User: Clicks "GPT-4o Mini"
Bot: ✅ Выбрана модель: GPT-4o Mini
     Напиши свой вопрос!

User: What is Python?
Bot: Python is a high-level programming language...
     ---
     🤖 Модель: GPT-4o Mini
     [Inline buttons for model switch]
```

## Architecture

### Module Structure
```
src/
├── bot/              # Bot core and handlers
├── llm/              # LLM providers
│   ├── dto/          # DTO classes for API requests
│   └── providers/    # Provider implementations
├── features/         # Bot features
│   └── day_01/       # Day 01 chat feature
├── utils/            # Utilities
└── main.py           # Entry point
```

### Key Components

- **BaseLLM**: Abstract interface for all LLM providers
- **BaseFeature**: Abstract interface for all features
- **FeatureRegistry**: Centralized feature management
- **LLMFactory**: Factory for creating LLM instances
- **ProxyAPI Integration**: Unified interface for all LLM providers

### LLM Providers

Currently supported:
- **GPT-4o Mini** via OpenAI API
- **Claude 3.5 Haiku** via Anthropic API

All providers use ProxyAPI as a unified endpoint.

## Development

### Adding a New LLM Provider

1. Create DTO classes in `src/llm/dto/your_provider.py`:
```python
from pydantic import BaseModel

class YourProviderRequest(BaseModel):
    model: str
    messages: List[dict]
    # other fields
```

2. Create provider in `src/llm/providers/your_provider.py`:
```python
from src.llm.base import BaseLLM

class YourProvider(BaseLLM):
    async def generate_response(self, prompt: str):
        # Implementation using ProxyAPI
        pass
```

3. Register in `LLMFactory`:
```python
LLMFactory.register_provider("your_provider", YourProvider)
```

4. Add configuration in `.env` and `config.py`

### Adding a New Feature

1. Create a new feature class in `src/features/`:
```python
from src.features.base import BaseFeature

class MyFeature(BaseFeature):
    @property
    def command(self) -> str:
        return "myfeature"
    
    async def handle_command(self, update, context):
        # Implementation
```

2. Register in main.py:
```python
my_feature = MyFeature(config)
registry.register(my_feature)
```

## Testing

Run tests:
```bash
pytest
```

With coverage:
```bash
pytest --cov=src --cov-report=html
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | Required |
| `PROXYAPI_API_KEY` | ProxyAPI key | Required |
| `OPENAI_MODEL` | OpenAI model ID | `gpt-4o-mini` |
| `OPENAI_DISPLAY_NAME` | Display name | `GPT-4o Mini` |
| `ANTHROPIC_MODEL` | Anthropic model ID | `claude-3-5-haiku-20241022` |
| `ANTHROPIC_DISPLAY_NAME` | Display name | `Claude 3.5 Haiku` |

## Roadmap

### Day 01 ✅
- [x] Basic bot structure
- [x] Multi-LLM support via ProxyAPI
- [x] Inline model selection buttons
- [x] Model information display
- [x] GPT-4o Mini and Claude 3.5 Haiku integration

### Future Days
- [ ] Additional LLM providers (YaGPT, GigaChat)
- [ ] Conversation history management
- [ ] Voice message support
- [ ] Image generation
- [ ] Web search integration
- [ ] Reminder and scheduling features

## License
MIT

## Contributing
Contributions are welcome! Please read the contributing guidelines first.

