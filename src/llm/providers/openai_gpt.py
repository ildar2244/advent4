"""OpenAI GPT provider implementation via ProxyAPI."""
import logging
from typing import AsyncGenerator

import aiohttp

from src.llm.base import BaseLLM
from src.llm.dto.openai import OpenAIMessage, OpenAIRequest
from src.llm.templates.json_templates import format_prompt_for_json_response
from src.utils.typing import LLMResponse

logger = logging.getLogger(__name__)


class OpenAIGPTProvider(BaseLLM):
    """OpenAI GPT provider using ProxyAPI."""
    
    def __init__(self, api_key: str, proxy_url: str, model: str, display_name: str):
        """Initialize OpenAI GPT provider.
        
        Args:
            api_key: ProxyAPI key
            proxy_url: ProxyAPI endpoint URL
            model: Model identifier (e.g., 'gpt-4o-mini')
            display_name: Display name for the model
        """
        super().__init__(name="gpt", display_name=display_name)
        self.api_key = api_key
        self.proxy_url = proxy_url
        self.model = model
        self.session: aiohttp.ClientSession = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def generate_response(self, prompt: str, json_format: bool = False) -> AsyncGenerator[LLMResponse, None]:
        """Generate response from OpenAI via ProxyAPI (non-streaming).
        
        Args:
            prompt: User's prompt/question
            json_format: Whether to require JSON format response
            
        Yields:
            LLMResponse: Complete response
            
        Raises:
            Exception: If API call fails
        """
        session = await self._get_session()
        
        # Prepare request
        if json_format:
            formatted_prompt = format_prompt_for_json_response(prompt)
        else:
            formatted_prompt = prompt
            
        messages = [OpenAIMessage(role="user", content=formatted_prompt)]
        request_data = OpenAIRequest(
            model=self.model,
            messages=messages,
            stream=False  # Disable streaming
        )
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
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
                    logger.error(f"OpenAI API error: {response.status} - {error_text}")
                    raise Exception(f"API error: {response.status}")
                
                # Parse the complete response
                response_data = await response.json()
                
                # Extract content from the response
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    choice = response_data['choices'][0]
                    if 'message' in choice and 'content' in choice['message']:
                        full_content = choice['message']['content']
                        
                        logger.info("=== FULL RESPONSE FROM OPENAI ===")
                        logger.info("Model: %s", self.display_name)
                        logger.info("JSON Format: %s", json_format)
                        logger.info("Response content:")
                        logger.info("%s", full_content)
                        logger.info("=== END FULL RESPONSE ===")
                        
                        # If JSON format was requested, validate and wrap the response
                        if json_format:
                            try:
                                import json
                                from src.llm.templates.json_templates import validate_json_response
                                validated_response = validate_json_response(full_content)
                                validated_json = json.dumps(validated_response, ensure_ascii=False)
                                logger.info("=== VALIDATED JSON RESPONSE ===")
                                logger.info("%s", validated_json)
                                logger.info("=== END VALIDATED JSON ===")
                                yield LLMResponse(
                                    content=validated_json,
                                    model_name=self.display_name,
                                    provider_name=self.name
                                )
                            except Exception as e:
                                logger.warning(f"JSON validation error: {e}")
                                yield LLMResponse(
                                    content=full_content,
                                    model_name=self.display_name,
                                    provider_name=self.name
                                )
                        else:
                            yield LLMResponse(
                                content=full_content,
                                model_name=self.display_name,
                                provider_name=self.name
                            )
                    else:
                        raise Exception("No content found in response")
                else:
                    raise Exception("No choices found in response")
                    
        except Exception as e:
            logger.error(f"OpenAI GPT API error: {e}", exc_info=True)
            raise
    
    async def generate_json_response(self, prompt: str) -> AsyncGenerator[LLMResponse, None]:
        """Generate response in JSON format from OpenAI via ProxyAPI.
        
        Args:
            prompt: User's prompt/question
            
        Yields:
            LLMResponse: Response chunks
            
        Raises:
            Exception: If API call fails
        """
        async for response in self.generate_response(prompt, json_format=True):
            yield response
    
    async def close(self):
        """Close the HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("OpenAI GPT session closed")

