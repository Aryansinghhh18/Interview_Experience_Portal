import json
import logging
from typing import Dict, Any, List, Optional
from services.ai.ai_factory import AIFactory
from dao.ai_dao import AIDaO
from dao.experience_dao import ExperienceDAO

logger = logging.getLogger(__name__)

class QuestionGenerationService:
    @staticmethod
    def generate_questions(company_name: str, job_role: str,
                           technical_domain: Optional[str] = None,
                           difficulty: str = "Intermediate",
                           category: str = "Technical",
                           count: int = 5,
                           user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        provider = AIFactory.get_provider()

        # Retrieve relevant approved interview experiences to use as context
        context_snippets = []
        try:
            approved_exps = ExperienceDAO.get_approved(company=company_name, limit=3)
            for exp in approved_exps:
                if exp.technical_questions:
                    context_snippets.append(f"Past Experience Questions ({exp.difficulty}): {exp.technical_questions[:300]}")
        except Exception as e:
            logger.warning(f"Could not load approved experiences for context: {e}")

        context_block = ""
        if context_snippets:
            context_block = "\nReal Company Interview Insights from Approved Experiences:\n" + "\n---\n".join(context_snippets) + "\n"

        domain_str = f"Technical Domain: {technical_domain}" if technical_domain else ""

        prompt = f"""
You are an expert technical interviewer and interview preparation coach.
Generate {count} high-quality, realistic interview practice questions.

Parameters:
- Target Company: {company_name}
- Job Role: {job_role}
{domain_str}
- Category: {category} (Options: Technical, HR, Scenario-based, Conceptual, Programming)
- Target Difficulty: {difficulty} (Beginner, Intermediate, Advanced)
{context_block}
Guidelines:
1. Questions should reflect realistic industry hiring patterns for {company_name} and {job_role}.
2. For each question, provide:
   - 'question': Clear, specific question text.
   - 'difficulty': Beginner, Intermediate, or Advanced.
   - 'category': The question type (Technical, HR, Scenario-based, Conceptual, or Programming).
   - 'topic': Specific subtopic (e.g. 'Dynamic Programming', 'SQL Optimization', 'Distributed Systems', 'Behavioral').
   - 'suggested_answer': A comprehensive, model candidate response.
   - 'explanation': Clear architectural or conceptual explanation of why this answer is effective.
   - 'key_concepts': Comma-separated list of 3-5 core principles/technologies the candidate should study.
3. Return ONLY a valid JSON object adhering strictly to the schema below.

Required JSON Schema:
{{
  "questions": [
    {{
      "question": "Question text...",
      "difficulty": "{difficulty}",
      "category": "{category}",
      "topic": "Specific Topic",
      "suggested_answer": "Model answer...",
      "explanation": "Why this question matters and detailed reasoning...",
      "key_concepts": "Concept A, Concept B, Concept C"
    }}
  ]
}}
"""
        res = provider.generate_json(
            prompt=prompt,
            schema_description="JSON object with 'questions' list containing question, difficulty, category, topic, suggested_answer, explanation, key_concepts"
        )

        AIDaO.log_ai_usage(
            user_id=user_id,
            feature_name="question_generator",
            provider=res.get('provider', 'unknown'),
            model_name=res.get('model', 'unknown'),
            status=res.get('status', 'error'),
            prompt_tokens=res.get('prompt_tokens', 0),
            completion_tokens=res.get('completion_tokens', 0),
            token_usage=res.get('total_tokens', 0),
            estimated_cost=AIFactory.calculate_cost(
                res.get('provider', ''), res.get('model', ''),
                res.get('prompt_tokens', 0), res.get('completion_tokens', 0)
            ),
            error_message=res.get('error')
        )

        if res['status'] == 'success' and isinstance(res.get('content'), dict):
            questions = res['content'].get('questions', [])
            if questions:
                return questions[:count]

        # Domain-aware fallback questions
        logger.warning("Using fallback questions for question generation")
        fallbacks = [
            {
                "question": f"How would you architect a scalable, fault-tolerant microservice for {job_role} at {company_name}?",
                "difficulty": difficulty,
                "category": "Technical",
                "topic": "System Design",
                "suggested_answer": "Break down services into bounded contexts, utilize an API Gateway, asynchronous message broker (Kafka/RabbitMQ) for decoupled event processing, circuit breaker patterns for resilience, and distributed tracing with OpenTelemetry.",
                "explanation": "Evaluates architectural decomposition, decoupling, and resilience against cascading failures in large scale production systems.",
                "key_concepts": "Microservices, Circuit Breaker, API Gateway, Asynchronous Messaging, Eventual Consistency"
            },
            {
                "question": f"What are the key trade-offs between SQL (Relational) and NoSQL (Document/Key-Value) databases for {company_name}'s high-throughput services?",
                "difficulty": difficulty,
                "category": "Conceptual",
                "topic": "Databases & Storage",
                "suggested_answer": "SQL offers ACID guarantees, normalized data modeling, and rich relational queries but scales vertically or requires sharding. NoSQL (e.g. Cassandra, DynamoDB, MongoDB) offers flexible schemas and horizontal partitioning at the cost of eventual consistency.",
                "explanation": "Tests deep understanding of CAP theorem, database storage engines, and appropriate technology selection based on access patterns.",
                "key_concepts": "CAP Theorem, ACID vs BASE, Indexing, Sharding, Replication Factor"
            },
            {
                "question": "Describe a scenario where you had to debug a production performance regression under tight latency constraints.",
                "difficulty": difficulty,
                "category": "Scenario-based",
                "topic": "Observability & Debugging",
                "suggested_answer": "Describe checking APM metrics, isolating CPU vs memory vs database wait time, taking thread/heap dumps, profiling query latency, applying a safe hotfix or rolling back, and documenting a blameless post-mortem.",
                "explanation": "Shows real-world incident response readiness, practical troubleshooting skills, and blameless engineering culture.",
                "key_concepts": "APM Profiling, Thread Dumps, Incident Management, Post-mortem Analysis"
            },
            {
                "question": "How do you handle merge conflicts, code reviews, and maintaining high test coverage in continuous integration pipelines?",
                "difficulty": "Intermediate",
                "category": "Technical",
                "topic": "CI/CD & DevOps",
                "suggested_answer": "Keep branches short-lived via trunk-based development or regular rebasing. Conduct thorough PR reviews focused on architecture and readability, and gate deployments with automated pytest/lint suites enforcing coverage thresholds.",
                "explanation": "Ensures the candidate adheres to robust modern software engineering standards.",
                "key_concepts": "Git Rebasing, Code Review Rubric, Automated Testing, CI/CD Gates"
            },
            {
                "question": f"Why are you specifically interested in the {job_role} position at {company_name}, and how do your technical values align with our engineering culture?",
                "difficulty": "Intermediate",
                "category": "HR",
                "topic": "Company Alignment",
                "suggested_answer": "Articulate genuine appreciation for the company's technical scale, product mission, and commitment to engineering excellence. Provide examples of how your personal work ethic and problem-solving align.",
                "explanation": "Assesses cultural addition, intrinsic motivation, and professional preparation for the specific employer.",
                "key_concepts": "STAR Method, Cultural Fit, Company Values, Career Trajectory"
            }
        ]
        return fallbacks[:count]
