import logging
import time
from typing import Dict, Any, Optional, List
from services.ai.base_provider import BaseAIProvider

logger = logging.getLogger(__name__)

class OpenAIProvider(BaseAIProvider):
    """OpenAI API Provider implementation."""

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gpt-4o-mini"):
        super().__init__(api_key=api_key, model_name=model_name or "gpt-4o-mini")
        self.provider_name = "openai"
        self._client = None
        self._init_client()

    def _init_client(self):
        if not self.api_key or self.api_key.strip() == "" or "your_openai_api_key" in self.api_key:
            return
        try:
            from openai import OpenAI
            self._client = OpenAI(api_key=self.api_key.strip())
            logger.info(f"Initialized OpenAI client with model {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            self._client = None

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip() and "your_openai_api_key" not in self.api_key and self._client)

    def generate_text(self, prompt: str, system_instruction: Optional[str] = None,
                      temperature: float = 0.7, max_tokens: int = 2048) -> Dict[str, Any]:
        if not self.is_configured():
            return {
                'content': None,
                'prompt_tokens': 0,
                'completion_tokens': 0,
                'total_tokens': 0,
                'model': self.model_name,
                'provider': self.provider_name,
                'status': 'error',
                'error': 'OpenAI API key is not configured. Please add OPENAI_API_KEY in your .env file.'
            }

        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        retries = 2
        for attempt in range(retries + 1):
            try:
                response = self._client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                choice = response.choices[0]
                text = choice.message.content or ""
                usage = response.usage
                p_tokens = usage.prompt_tokens if usage else len(prompt) // 4
                c_tokens = usage.completion_tokens if usage else len(text) // 4

                return {
                    'content': text,
                    'prompt_tokens': p_tokens,
                    'completion_tokens': c_tokens,
                    'total_tokens': p_tokens + c_tokens,
                    'model': self.model_name,
                    'provider': self.provider_name,
                    'status': 'success',
                    'error': None
                }
            except Exception as e:
                logger.error(f"OpenAI attempt {attempt + 1} failed: {e}")
                if attempt < retries:
                    time.sleep(1.0 * (attempt + 1))
                else:
                    return {
                        'content': None,
                        'prompt_tokens': 0,
                        'completion_tokens': 0,
                        'total_tokens': 0,
                        'model': self.model_name,
                        'provider': self.provider_name,
                        'status': 'error',
                        'error': str(e)
                    }

    def generate_json(self, prompt: str, schema_description: Optional[str] = None,
                      system_instruction: Optional[str] = None, temperature: float = 0.2) -> Dict[str, Any]:
        if not self.is_configured():
            return {
                'content': None,
                'prompt_tokens': 0,
                'completion_tokens': 0,
                'total_tokens': 0,
                'model': self.model_name,
                'provider': self.provider_name,
                'status': 'error',
                'error': 'OpenAI API key is not configured. Please add OPENAI_API_KEY in your .env file.'
            }

        sys_prompt = "You are a specialized AI assistant that outputs STRICT JSON adhering to specifications."
        if schema_description:
            sys_prompt += f"\nRequired JSON schema:\n{schema_description}"
        if system_instruction:
            sys_prompt = f"{system_instruction}\n{sys_prompt}"

        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": prompt}
        ]

        retries = 2
        for attempt in range(retries + 1):
            try:
                response = self._client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=temperature,
                    response_format={"type": "json_object"}
                )
                raw_text = response.choices[0].message.content or "{}"
                usage = response.usage
                p_tokens = usage.prompt_tokens if usage else len(prompt) // 4
                c_tokens = usage.completion_tokens if usage else len(raw_text) // 4

                parsed_data = self._safe_parse_json(raw_text)
                if parsed_data is None:
                    return {
                        'content': None,
                        'raw_text': raw_text,
                        'prompt_tokens': p_tokens,
                        'completion_tokens': c_tokens,
                        'total_tokens': p_tokens + c_tokens,
                        'model': self.model_name,
                        'provider': self.provider_name,
                        'status': 'error',
                        'error': 'Failed to parse JSON response.'
                    }

                return {
                    'content': parsed_data,
                    'raw_text': raw_text,
                    'prompt_tokens': p_tokens,
                    'completion_tokens': c_tokens,
                    'total_tokens': p_tokens + c_tokens,
                    'model': self.model_name,
                    'provider': self.provider_name,
                    'status': 'success',
                    'error': None
                }
            except Exception as e:
                logger.error(f"OpenAI JSON attempt {attempt + 1} failed: {e}")
                if attempt < retries:
                    time.sleep(1.0 * (attempt + 1))
                else:
                    return {
                        'content': None,
                        'prompt_tokens': 0,
                        'completion_tokens': 0,
                        'total_tokens': 0,
                        'model': self.model_name,
                        'provider': self.provider_name,
                        'status': 'error',
                        'error': str(e)
                    }

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        if not self.is_configured():
            logger.warning("OpenAI API not configured for embeddings.")
            return []
        try:
            res = self._client.embeddings.create(
                model="text-embedding-3-small",
                input=texts
            )
            return [d.embedding for d in res.data]
        except Exception as e:
            logger.error(f"OpenAI embedding error: {e}")
            return []
