import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from config import Config
from services.ai.ai_factory import AIFactory
from dao.ai_dao import AIDaO

logger = logging.getLogger(__name__)

class ResumeAnalysisService:
    @staticmethod
    def extract_text_from_file(file_path: Path) -> str:
        """Extract text from PDF or DOCX file using PyMuPDF or python-docx."""
        ext = file_path.suffix.lower()
        text_content = []

        if ext == '.pdf':
            try:
                import pymupdf
                doc = pymupdf.open(str(file_path))
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    text_content.append(page.get_text("text"))
                doc.close()
            except Exception as e:
                logger.error(f"PyMuPDF error reading {file_path}: {e}")
                raise ValueError(f"Failed to extract text from PDF: {e}")
        elif ext in ('.docx', '.doc'):
            try:
                import docx
                doc = docx.Document(str(file_path))
                for para in doc.paragraphs:
                    if para.text.strip():
                        text_content.append(para.text)
                for table in doc.tables:
                    for row in table.rows:
                        row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                        if row_text:
                            text_content.append(" | ".join(row_text))
            except Exception as e:
                logger.error(f"python-docx error reading {file_path}: {e}")
                raise ValueError(f"Failed to extract text from DOCX: {e}")
        else:
            raise ValueError(f"Unsupported file format: {ext}")

        extracted_text = "\n".join(text_content).strip()
        if not extracted_text:
            raise ValueError("The uploaded document contains no readable text (it may be a scanned image).")
            
        return extracted_text

    @staticmethod
    def analyze_resume(resume_text: str, target_job_role: str,
                       job_description: Optional[str] = None,
                       user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Analyze extracted resume against target job role and optional job description.
        """
        provider = AIFactory.get_provider()

        # Sanitize and truncate resume text to safe processing window (e.g., first 10,000 chars)
        truncated_resume = resume_text[:10000]
        jd_block = ""
        if job_description and job_description.strip():
            jd_block = f"\nSpecific Target Job Description:\n\"\"\"{job_description.strip()[:4000]}\"\"\"\n"

        prompt = f"""
You are an expert technical talent evaluator, senior engineering recruiter, and resume coach.
Analyze the following candidate's resume strictly against the target job role and requirements.

Target Job Role: {target_job_role}
{jd_block}
Candidate's Resume Text:
\"\"\"{truncated_resume}\"\"\"

Critical Evaluation Rules:
1. DO NOT invent qualifications, skills, degrees, or companies that are not explicitly present in the resume text.
2. Clearly distinguish between missing essential skills and underrepresented skills.
3. Treat the compatibility_score (0.0 to 100.0) as an AI-generated heuristic estimate of resume alignment, NOT an objective guarantee of hiring.
4. Extract skills as a clean, deduplicated JSON list of technology names.
5. Provide high-impact, actionable resume improvement suggestions (formatting, metrics, clarity, missing sections).
6. Provide recommended technical topics the candidate should master to become more competitive for {target_job_role}.
7. Return ONLY a valid JSON object adhering strictly to the schema below.

Required JSON Schema:
{{
  "skills": ["Python", "Flask", "SQL", "Git", "Docker"],
  "education_summary": "Bachelor of Technology in Computer Science (2020-2024)...",
  "projects_summary": "Summary of prominent technical projects listed in the resume...",
  "experience_summary": "Summary of prior internships, full-time positions, or open source contributions...",
  "strengths": ["Clear breakdown of backend architecture", "Hands-on relational database experience"],
  "weaknesses": ["Lack of quantifiable metrics or production scale indicators", "No mention of automated testing"],
  "missing_skills": ["Kubernetes", "Redis", "Cloud Platform (AWS/GCP/Azure)"],
  "compatibility_score": 78.5,
  "improvement_suggestions": [
    "Quantify project achievements using metrics (e.g., 'Reduced API response times by 35%').",
    "Add a dedicated 'Technical Skills' section categorizing Languages, Frameworks, and Tools.",
    "Include direct links to deployed applications and active GitHub repositories."
  ],
  "suggested_topics": [
    "Distributed Systems & Caching (Redis/Memcached)",
    "Containerization & CI/CD Pipelines (Docker, GitHub Actions)",
    "Database Indexing & Query Plan Optimization"
  ]
}}
"""
        res = provider.generate_json(
            prompt=prompt,
            schema_description="JSON object with skills, education_summary, projects_summary, experience_summary, strengths, weaknesses, missing_skills, compatibility_score, improvement_suggestions, suggested_topics"
        )

        AIDaO.log_ai_usage(
            user_id=user_id,
            feature_name="resume_analyzer",
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
            c = res['content']
            try:
                score = float(c.get('compatibility_score', 75.0))
                return {
                    "skills": c.get('skills', []),
                    "education_summary": str(c.get('education_summary', 'Education details extracted from resume.')),
                    "projects_summary": str(c.get('projects_summary', 'Project details extracted from resume.')),
                    "experience_summary": str(c.get('experience_summary', 'Experience details extracted from resume.')),
                    "strengths": c.get('strengths', []),
                    "weaknesses": c.get('weaknesses', []),
                    "missing_skills": c.get('missing_skills', []),
                    "compatibility_score": min(max(score, 0.0), 100.0),
                    "improvement_suggestions": c.get('improvement_suggestions', []),
                    "suggested_topics": c.get('suggested_topics', [])
                }
            except Exception as e:
                logger.error(f"Error parsing resume analysis content: {e}")

        # Rule-based fallback analysis if AI provider fails or is unconfigured
        logger.warning("Using rule-based resume analysis fallback")
        known_skills = ["Python", "Java", "C++", "JavaScript", "HTML", "CSS", "SQL", "MySQL", 
                        "PostgreSQL", "Flask", "Django", "React", "Node.js", "Docker", "Git", 
                        "Linux", "AWS", "Machine Learning", "Data Structures", "Algorithms"]
        found_skills = [s for s in known_skills if re.search(rf"\b{re.escape(s)}\b", resume_text, re.IGNORECASE)]
        
        missing = ["Cloud Architecture (AWS/GCP)", "CI/CD Pipelines", "Container Orchestration (Kubernetes)"]
        missing_filtered = [m for m in missing if not any(k.lower() in resume_text.lower() for k in m.split())]

        calc_score = min(50.0 + len(found_skills) * 4.0, 85.0)

        return {
            "skills": found_skills or ["General Software Engineering", "Problem Solving", "Web Development"],
            "education_summary": "Academic qualifications and technical coursework identified in resume.",
            "projects_summary": "Application development and technical assignments detailed in candidate resume.",
            "experience_summary": "Work history, internships, and collaborative software projects.",
            "strengths": [
                f"Demonstrated proficiency in {', '.join(found_skills[:4]) if found_skills else 'core programming languages'}",
                "Structured layout and clear representation of software projects"
            ],
            "weaknesses": [
                "Could include more quantifiable business outcomes and performance benchmarks",
                "Certifications or cloud deployment experience could be highlighted more prominently"
            ],
            "missing_skills": missing_filtered,
            "compatibility_score": round(calc_score, 1),
            "improvement_suggestions": [
                "Quantify bullet points: instead of 'Built website', use 'Engineered Flask web application serving 500+ daily requests with 99.8% uptime'.",
                "Ensure standard section headings: Education, Technical Skills, Projects, Experience.",
                "Tailor keywords directly to match the job description of " + target_job_role
            ],
            "suggested_topics": [
                "System Architecture & Scaling Patterns",
                "Automated Testing (Unit, Integration, E2E)",
                "Microservice Communication & Message Queues"
            ]
        }
