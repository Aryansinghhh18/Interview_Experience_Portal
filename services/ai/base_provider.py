import abc
import json
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class BaseAIProvider(abc.ABC):
    """Abstract Base Class for AI Model Providers (Gemini, OpenAI, etc.)."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key
        self.model_name = model_name

    @abc.abstractmethod
    def is_configured(self) -> bool:
        """Return True if credentials and configuration are valid."""
        pass

    @abc.abstractmethod
    def generate_text(self, prompt: str, system_instruction: Optional[str] = None,
                      temperature: float = 0.7, max_tokens: int = 2048) -> Dict[str, Any]:
        """
        Generate plain text response.
        Returns dict with keys: content, prompt_tokens, completion_tokens, total_tokens, model, provider, status, error
        """
        pass

    @abc.abstractmethod
    def generate_json(self, prompt: str, schema_description: Optional[str] = None,
                      system_instruction: Optional[str] = None, temperature: float = 0.3) -> Dict[str, Any]:
        """
        Generate structured JSON response.
        Returns dict with keys: content (parsed json object), raw_text, prompt_tokens, completion_tokens, total_tokens, model, provider, status, error
        """
        pass

    @abc.abstractmethod
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate vector embeddings for input texts."""
        pass

    def _clean_json_markdown(self, text: str) -> str:
        """Strip ```json ... ``` markdown fencing if present."""
        cleaned = text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        return cleaned.strip()

    def _safe_parse_json(self, text: str) -> Optional[Any]:
        """Safely parse JSON from raw string."""
        cleaned = self._clean_json_markdown(text)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}. Raw content: {cleaned[:200]}")
            # Try finding first { or [ and last } or ]
            start_curly = cleaned.find("{")
            end_curly = cleaned.rfind("}")
            if start_curly != -1 and end_curly != -1 and end_curly > start_curly:
                try:
                    return json.loads(cleaned[start_curly:end_curly + 1])
                except Exception:
                    pass
            start_sq = cleaned.find("[")
            end_sq = cleaned.rfind("]")
            if start_sq != -1 and end_sq != -1 and end_sq > start_sq:
                try:
                    return json.loads(cleaned[start_sq:end_sq + 1])
                except Exception:
                    pass
            return None
