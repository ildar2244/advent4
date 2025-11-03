"""Anthropic Claude provider implementation via ProxyAPI."""
import logging
from typing import AsyncGenerator

import aiohttp

from src.llm.base import BaseLLM
from src.llm.dto.anthropic import AnthropicMessage, AnthropicRequest
from src.utils.typing import LLMResponse

logger = logging.getLogger(__name__)


class AnthropicClaudeProvider(BaseLLM):
    """Anthropic Claude provider using ProxyAPI."""
    
    def __init__(self, api_key: str, proxy_url: str, model: str, display_name: str):
        """Initialize Anthropic Claude provider.
        
        Args:
            api_key: ProxyAPI key
            proxy_url: ProxyAPI endpoint URL
            model: Model identifier (e.g., 'claude-3-5-haiku-20241022')
            display_name: Display name for the model
        """
        super().__init__(name="claude", display_name=display_name)
        self.api_key = api_key
        self.proxy_url = proxy_url
        self.model = model
        self.session: aiohttp.ClientSession = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def generate_response(self, prompt: str) -> AsyncGenerator[LLMResponse, None]:
        """Generate streaming response from Claude via ProxyAPI.
        
        Args:
            prompt: User's prompt/question
            
        Yields:
            LLMResponse: Response chunks
            
        Raises:
            Exception: If API call fails
        """
        session = await self._get_session()
        
        # Prepare request
        messages = [AnthropicMessage(role="user", content=prompt)]
        request_data = AnthropicRequest(
            model=self.model,
            messages=messages,
            stream=True
        )
        
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        try:
            logger.info(f"Generating response with {self.display_name}")
            
            async with session.post(
                self.proxy_url,
                json=request_data.model_dump(),
                headers=headers
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Anthropic API error: {response.status} - {error_text}")
                    raise Exception(f"API error: {response.status}")
                
                full_content = ""
                async for line in response.content:
                    if line:
                        try:
                            # Parse SSE format
                            decoded = line.decode('utf-8')
                            if decoded.startswith('data: '):
                                data_str = decoded[6:].strip()
                                if data_str == '[DONE]':
                                    break
                                
                                # Parse JSON chunk
                                import json
                                chunk_data = json.loads(data_str)
                                
                                # Extract content from Anthropic format
                                if 'delta' in chunk_data:
                                    delta = chunk_data['delta']
                                    if 'text' in delta:
                                        content_chunk = delta['text']
                                        full_content += content_chunk
                                        yield LLMResponse(
                                            content=content_chunk,
                                            model_name=self.display_name,
                                            provider_name=self.name
                                        )
                                elif 'content_block' in chunk_data:
                                    # Handle content block type
                                    if chunk_data['content_block']['type'] == 'text':
                                        content_chunk = chunk_data['content_block']['text']
                                        full_content += content_chunk
                                        yield LLMResponse(
                                            content=content_chunk,
                                            model_name=self.display_name,
                                            provider_name=self.name
                                        )
                        except Exception as e:
                            logger.warning(f"Error parsing chunk: {e}")
                            continue
                
                # Final complete response
                if full_content:
                    yield LLMResponse(
                        content=full_content,
                        model_name=self.display_name,
                        provider_name=self.name
                    )
                    
        except Exception as e:
            logger.error(f"Anthropic Claude API error: {e}", exc_info=True)
            raise
    
    async def close(self):
        """Close the HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("Anthropic Claude session closed")

