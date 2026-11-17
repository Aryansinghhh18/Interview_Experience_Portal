import logging
from typing import Optional, Dict, Any, List
from config import Config
from services.ai.base_provider import BaseAIProvider
from services.ai.gemini_provider import GeminiProvider
from services.ai.openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)

class MockAIProvider(BaseAIProvider):
    """
    Mock AI Provider for automated tests or local offline execution.
    Produces deterministic structured responses without requiring API keys or network access.
    """
    def __init__(self):
        super().__init__(api_key="mock-key", model_name="mock-model-v1")
        self.provider_name = "mock"

    def is_configured(self) -> bool:
        return True

    def generate_text(self, prompt: str, system_instruction: Optional[str] = None,
                      temperature: float = 0.7, max_tokens: int = 2048) -> Dict[str, Any]:
        return {
            'content': f"Mock AI Response for: {prompt[:80]}...",
            'prompt_tokens': 50,
            'completion_tokens': 30,
            'total_tokens': 80,
            'model': self.model_name,
            'provider': self.provider_name,
            'status': 'success',
            'error': None
        }

    def generate_json(self, prompt: str, schema_description: Optional[str] = None,
                      system_instruction: Optional[str] = None, temperature: float = 0.2) -> Dict[str, Any]:
        # Detect what type of JSON is being requested based on prompt keywords
        prompt_lower = prompt.lower()
        if "mock interview" in prompt_lower or "evaluate the user's answer" in prompt_lower:
            data = {
                "relevance_score": 85.0,
                "correctness_score": 82.0,
                "completeness_score": 80.0,
                "clarity_score": 90.0,
                "overall_score": 84.0,
                "strengths": "Clearly articulated the core concepts with appropriate technical terms.",
                "weaknesses": "Could have included an edge-case example or time complexity tradeoff.",
                "feedback": "Strong answer demonstrating good conceptual understanding.",
                "suggested_answer": "A comprehensive answer would detail time/space complexity and corner cases."
            }
        elif "final interview report" in prompt_lower or "overall performance evaluation" in prompt_lower:
            data = {
                "overall_score": 85.0,
                "final_feedback": "Commendable interview performance displaying solid core fundamentals.",
                "strengths_summary": "Quick problem decomposition, strong clarity in explanation, good structural thinking.",
                "weaknesses_summary": "Slight hesitation on system scaling tradeoffs and asymptotic bounds.",
                "recommendations": "Practice explaining distributed concurrency models and caching strategies."
            }
        elif "generate" in prompt_lower and "question" in prompt_lower:
            data = {
                "questions": [
                    {
                        "question": "How does the Python Global Interpreter Lock (GIL) impact multithreaded CPU-bound operations?",
                        "difficulty": "Intermediate",
                        "category": "Technical",
                        "topic": "Python Concurrency",
                        "suggested_answer": "The GIL ensures only one native thread executes Python bytecode at once. For CPU-bound tasks, multiprocessing or C extensions bypass this bottleneck.",
                        "explanation": "Fundamental mechanism in CPython memory management preventing race conditions.",
                        "key_concepts": "CPython GIL, Threading vs Multiprocessing, CPU-bound vs IO-bound tasks"
                    },
                    {
                        "question": "Explain database indexing and compare B-Tree vs Hash indexing.",
                        "difficulty": "Intermediate",
                        "category": "Technical",
                        "topic": "Database Systems",
                        "suggested_answer": "B-Tree indexes support range queries (BETWEEN, >, <) in O(log N) time, while Hash indexes offer O(1) point lookups but cannot do range searches.",
                        "explanation": "Storage engine data structures heavily dictate read vs write query performance.",
                        "key_concepts": "B-Trees, Hash Indexes, Composite Keys, Clustered vs Secondary Indexes"
                    }
                ]
            }
        elif "resume" in prompt_lower:
            data = {
                "skills": ["Python", "Flask", "SQL", "Git", "REST APIs", "Docker"],
                "education_summary": "Bachelor of Technology in Computer Science with strong academic record.",
                "projects_summary": "Built multiple web applications, API microservices, and database systems.",
                "experience_summary": "Internship and project experience developing backend services and user interfaces.",
                "strengths": ["Strong foundational Python skills", "Hands-on database management experience"],
                "weaknesses": ["Limited cloud deployment metrics on resume", "Lack of quantified project impact metrics"],
                "missing_skills": ["Kubernetes", "AWS / Cloud Infrastructure", "CI/CD Pipeline tools"],
                "compatibility_score": 82.5,
                "improvement_suggestions": [
                    "Add quantifiable impact metrics to project descriptions (e.g., 'reduced query latency by 40%').",
                    "Include links to live project demos or open-source GitHub repositories.",
                    "Highlight unit testing and automated CI/CD practices."
                ],
                "suggested_topics": ["Docker & Kubernetes Orchestration", "System Design & Microservices", "AWS ECS / Lambda"]
            }
        else:
            data = {"status": "ok", "message": "Mock structured response"}

        return {
            'content': data,
            'raw_text': str(data),
            'prompt_tokens': 60,
            'completion_tokens': 120,
            'total_tokens': 180,
            'model': self.model_name,
            'provider': self.provider_name,
            'status': 'success',
            'error': None
        }

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        # Return deterministic dummy vector of dimension 384
        import hashlib
        vectors = []
        for text in texts:
            seed = int(hashlib.md5(text.encode('utf-8')).hexdigest()[:8], 16)
            # deterministic 384-dim pseudo random numbers
            import random
            rng = random.Random(seed)
            vectors.append([rng.uniform(-1.0, 1.0) for _ in range(384)])
        return vectors


class AIFactory:
    """Factory to instantiate and retrieve configured AI providers."""
    
    _instances: Dict[str, BaseAIProvider] = {}
    _force_mock: bool = False

    @classmethod
    def set_force_mock(cls, force: bool = True):
        cls._force_mock = force

    @classmethod
    def get_provider(cls, provider_type: Optional[str] = None) -> BaseAIProvider:
        if cls._force_mock:
            return MockAIProvider()

        provider_name = (provider_type or Config.AI_PROVIDER).lower().strip()
        
        if provider_name in cls._instances:
            return cls._instances[provider_name]

        if provider_name == "gemini":
            provider = GeminiProvider(
                api_key=Config.GEMINI_API_KEY,
                model_name=Config.GEMINI_MODEL
            )
        elif provider_name == "openai":
            provider = OpenAIProvider(
                api_key=Config.OPENAI_API_KEY,
                model_name=Config.OPENAI_MODEL
            )
        elif provider_name == "mock":
            provider = MockAIProvider()
        else:
            logger.warning(f"Unknown AI provider '{provider_name}'. Defaulting to Gemini.")
            provider = GeminiProvider(
                api_key=Config.GEMINI_API_KEY,
                model_name=Config.GEMINI_MODEL
            )

        cls._instances[provider_name] = provider
        return provider

    @staticmethod
    def calculate_cost(provider: str, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Estimate cost in USD based on standard published pricing."""
        # Standard approximate rates per 1M tokens
        # Gemini 2.5 Flash: ~$0.075 / 1M prompt, $0.30 / 1M completion
        # GPT-4o-mini: ~$0.15 / 1M prompt, $0.60 / 1M completion
        provider_lower = provider.lower()
        if "gemini" in provider_lower:
            prompt_rate = 0.075 / 1_000_000
            completion_rate = 0.30 / 1_000_000
        elif "openai" in provider_lower or "gpt" in model.lower():
            prompt_rate = 0.15 / 1_000_000
            completion_rate = 0.60 / 1_000_000
        else:
            prompt_rate = 0.05 / 1_000_000
            completion_rate = 0.15 / 1_000_000

        cost = (prompt_tokens * prompt_rate) + (completion_tokens * completion_rate)
        return round(cost, 6)
