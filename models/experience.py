class InterviewExperience:
    def __init__(self, id=None, user_id=None, company_id=None, job_role=None, interview_date=None,
                 interview_type='Online', difficulty='Medium', experience_level='Fresher',
                 interview_rounds=1, technical_questions=None, hr_questions=None,
                 overall_experience=None, preparation_tips=None, result='Not Disclosed',
                 approval_status='pending', rejection_reason=None, created_at=None, updated_at=None,
                 company_name=None, user_name=None):
        self.id = id
        self.user_id = user_id
        self.company_id = company_id
        self.job_role = job_role
        self.interview_date = interview_date
        self.interview_type = interview_type
        self.difficulty = difficulty
        self.experience_level = experience_level
        self.interview_rounds = interview_rounds
        self.technical_questions = technical_questions
        self.hr_questions = hr_questions
        self.overall_experience = overall_experience
        self.preparation_tips = preparation_tips
        self.result = result
        self.approval_status = approval_status
        self.rejection_reason = rejection_reason
        self.created_at = created_at
        self.updated_at = updated_at
        self.company_name = company_name
        self.user_name = user_name

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'company_id': self.company_id,
            'job_role': self.job_role,
            'interview_date': str(self.interview_date) if self.interview_date else None,
            'interview_type': self.interview_type,
            'difficulty': self.difficulty,
            'experience_level': self.experience_level,
            'interview_rounds': self.interview_rounds,
            'technical_questions': self.technical_questions,
            'hr_questions': self.hr_questions,
            'overall_experience': self.overall_experience,
            'preparation_tips': self.preparation_tips,
            'result': self.result,
            'approval_status': self.approval_status,
            'rejection_reason': self.rejection_reason,
            'created_at': str(self.created_at) if self.created_at else None,
            'company_name': self.company_name,
            'user_name': self.user_name
        }

    @classmethod
    def from_dict(cls, data):
        if not data:
            return None
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            company_id=data.get('company_id'),
            job_role=data.get('job_role'),
            interview_date=data.get('interview_date'),
            interview_type=data.get('interview_type', 'Online'),
            difficulty=data.get('difficulty', 'Medium'),
            experience_level=data.get('experience_level', 'Fresher'),
            interview_rounds=data.get('interview_rounds', 1),
            technical_questions=data.get('technical_questions'),
            hr_questions=data.get('hr_questions'),
            overall_experience=data.get('overall_experience'),
            preparation_tips=data.get('preparation_tips'),
            result=data.get('result', 'Not Disclosed'),
            approval_status=data.get('approval_status', 'pending'),
            rejection_reason=data.get('rejection_reason'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            company_name=data.get('company_name'),
            user_name=data.get('user_name')
        )
