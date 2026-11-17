import logging
import time
from typing import Dict, Any, Optional, List
from services.ai.base_provider import BaseAIProvider

logger = logging.getLogger(__name__)

class GeminiProvider(BaseAIProvider):
    """Google Gemini AI Provider implementation."""

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.5-flash"):
        super().__init__(api_key=api_key, model_name=model_name or "gemini-2.5-flash")
        self.provider_name = "gemini"
        self._client = None
        self._init_client()

    def _init_client(self):
        if not self.api_key or self.api_key.strip() == "" or "your_gemini_api_key" in self.api_key:
            return
        
        # Try google.genai first
        try:
            from google import genai
            self._client = genai.Client(api_key=self.api_key.strip())
            self._sdk_type = "genai"
            logger.info(f"Initialized google.genai client with model {self.model_name}")
            return
        except Exception as e:
            logger.warning(f"Could not initialize google.genai: {e}. Trying google.generativeai fallback.")

        # Fallback to google.generativeai
        try:
            import google.generativeai as gai
            gai.configure(api_key=self.api_key.strip())
            self._client = gai.GenerativeModel(self.model_name)
            self._sdk_type = "generativeai"
            logger.info(f"Initialized google.generativeai client with model {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini SDK: {e}")
            self._client = None

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip() and "your_gemini_api_key" not in self.api_key and self._client)

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
                'error': 'Gemini API key is not configured. Please add GEMINI_API_KEY in your .env file.'
            }

        retries = 2
        for attempt in range(retries + 1):
            try:
                if self._sdk_type == "genai":
                    config = {
                        "temperature": temperature,
                        "max_output_tokens": max_tokens,
                    }
                    if system_instruction:
                        config["system_instruction"] = system_instruction
                    
                    response = self._client.models.generate_content(
                        model=self.model_name,
                        contents=prompt,
                        config=config
                    )
                    text = response.text or ""
                    tokens = getattr(response, 'usage_metadata', None)
                    p_tokens = getattr(tokens, 'prompt_token_count', len(prompt) // 4) if tokens else len(prompt) // 4
                    c_tokens = getattr(tokens, 'candidates_token_count', len(text) // 4) if tokens else len(text) // 4
                else:
                    response = self._client.generate_content(
                        prompt,
                        generation_config={"temperature": temperature, "max_output_tokens": max_tokens}
                    )
                    text = response.text or ""
                    p_tokens = len(prompt) // 4
                    c_tokens = len(text) // 4

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
                logger.error(f"Gemini API attempt {attempt + 1} failed: {e}")
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
        json_instruction = (
            "You are a strict JSON generator. Your response must be ONLY valid raw JSON matching the required schema. "
            "Do not include any markdown fences, explanation, preamble, or commentary.\n"
        )
        if schema_description:
            json_instruction += f"\nRequired JSON Schema/Structure:\n{schema_description}\n"
        if system_instruction:
            full_system = f"{system_instruction}\n{json_instruction}"
        else:
            full_system = json_instruction

        res = self.generate_text(prompt=prompt, system_instruction=full_system, temperature=temperature)
        if res['status'] != 'success' or not res['content']:
            return res

        raw_text = res['content']
        parsed_data = self._safe_parse_json(raw_text)
        if parsed_data is None:
            return {
                **res,
                'status': 'error',
                'error': f'Failed to parse valid JSON from AI response: {raw_text[:150]}...',
                'raw_text': raw_text
            }

        res['content'] = parsed_data
        res['raw_text'] = raw_text
        return res

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        if not self.is_configured():
            logger.warning("Gemini API not configured for embeddings.")
            return []
        try:
            if self._sdk_type == "genai":
                embeddings = []
                for t in texts:
                    res = self._client.models.embed_content(
                        model="text-embedding-004",
                        contents=t
                    )
                    embeddings.append(res.embedding.values)
                return embeddings
        except Exception as e:
            logger.error(f"Gemini embedding error: {e}")
        return []
