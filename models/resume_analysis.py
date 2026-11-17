class ResumeAnalysis:
    def __init__(self, id=None, user_id=None, original_filename=None, target_job_role=None,
                 job_description=None, extracted_text_reference=None, skills=None,
                 education_summary=None, projects_summary=None, experience_summary=None,
                 strengths=None, weaknesses=None, missing_skills=None,
                 compatibility_score=None, improvement_suggestions=None, suggested_topics=None,
                 created_at=None):
        self.id = id
        self.user_id = user_id
        self.original_filename = original_filename
        self.target_job_role = target_job_role
        self.job_description = job_description
        self.extracted_text_reference = extracted_text_reference
        self.skills = skills
        self.education_summary = education_summary
        self.projects_summary = projects_summary
        self.experience_summary = experience_summary
        self.strengths = strengths
        self.weaknesses = weaknesses
        self.missing_skills = missing_skills
        self.compatibility_score = float(compatibility_score) if compatibility_score is not None else None
        self.improvement_suggestions = improvement_suggestions
        self.suggested_topics = suggested_topics
        self.created_at = created_at

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'original_filename': self.original_filename,
            'target_job_role': self.target_job_role,
            'job_description': self.job_description,
            'extracted_text_reference': self.extracted_text_reference,
            'skills': self.skills,
            'education_summary': self.education_summary,
            'projects_summary': self.projects_summary,
            'experience_summary': self.experience_summary,
            'strengths': self.strengths,
            'weaknesses': self.weaknesses,
            'missing_skills': self.missing_skills,
            'compatibility_score': self.compatibility_score,
            'improvement_suggestions': self.improvement_suggestions,
            'suggested_topics': self.suggested_topics,
            'created_at': str(self.created_at) if self.created_at else None
        }

    @classmethod
    def from_dict(cls, data):
        if not data:
            return None
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            original_filename=data.get('original_filename'),
            target_job_role=data.get('target_job_role'),
            job_description=data.get('job_description'),
            extracted_text_reference=data.get('extracted_text_reference'),
            skills=data.get('skills'),
            education_summary=data.get('education_summary'),
            projects_summary=data.get('projects_summary'),
            experience_summary=data.get('experience_summary'),
            strengths=data.get('strengths'),
            weaknesses=data.get('weaknesses'),
            missing_skills=data.get('missing_skills'),
            compatibility_score=data.get('compatibility_score'),
            improvement_suggestions=data.get('improvement_suggestions'),
            suggested_topics=data.get('suggested_topics'),
            created_at=data.get('created_at')
        )


class GeneratedQuestion:
    def __init__(self, id=None, user_id=None, company_name=None, job_role=None,
                 technical_domain=None, category='Technical', difficulty='Intermediate',
                 question=None, suggested_answer=None, explanation=None, key_concepts=None,
                 created_at=None, is_saved=False):
        self.id = id
        self.user_id = user_id
        self.company_name = company_name
        self.job_role = job_role
        self.technical_domain = technical_domain
        self.category = category
        self.difficulty = difficulty
        self.question = question
        self.suggested_answer = suggested_answer
        self.explanation = explanation
        self.key_concepts = key_concepts
        self.created_at = created_at
        self.is_saved = is_saved

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'company_name': self.company_name,
            'job_role': self.job_role,
            'technical_domain': self.technical_domain,
            'category': self.category,
            'difficulty': self.difficulty,
            'question': self.question,
            'suggested_answer': self.suggested_answer,
            'explanation': self.explanation,
            'key_concepts': self.key_concepts,
            'created_at': str(self.created_at) if self.created_at else None,
            'is_saved': self.is_saved
        }

    @classmethod
    def from_dict(cls, data):
        if not data:
            return None
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            company_name=data.get('company_name'),
            job_role=data.get('job_role'),
            technical_domain=data.get('technical_domain'),
            category=data.get('category'),
            difficulty=data.get('difficulty', 'Intermediate'),
            question=data.get('question'),
            suggested_answer=data.get('suggested_answer'),
            explanation=data.get('explanation'),
            key_concepts=data.get('key_concepts'),
            created_at=data.get('created_at'),
            is_saved=bool(data.get('is_saved', False))
        )
