class MockInterviewSession:
    def __init__(self, id=None, user_id=None, company_name=None, job_role=None,
                 interview_category='Technical', difficulty='Intermediate',
                 total_questions=5, current_question_index=0, overall_score=None,
                 final_feedback=None, strengths_summary=None, weaknesses_summary=None,
                 recommendations=None, status='in_progress', created_at=None, completed_at=None):
        self.id = id
        self.user_id = user_id
        self.company_name = company_name
        self.job_role = job_role
        self.interview_category = interview_category
        self.difficulty = difficulty
        self.total_questions = total_questions
        self.current_question_index = current_question_index
        self.overall_score = float(overall_score) if overall_score is not None else None
        self.final_feedback = final_feedback
        self.strengths_summary = strengths_summary
        self.weaknesses_summary = weaknesses_summary
        self.recommendations = recommendations
        self.status = status
        self.created_at = created_at
        self.completed_at = completed_at

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'company_name': self.company_name,
            'job_role': self.job_role,
            'interview_category': self.interview_category,
            'difficulty': self.difficulty,
            'total_questions': self.total_questions,
            'current_question_index': self.current_question_index,
            'overall_score': self.overall_score,
            'final_feedback': self.final_feedback,
            'strengths_summary': self.strengths_summary,
            'weaknesses_summary': self.weaknesses_summary,
            'recommendations': self.recommendations,
            'status': self.status,
            'created_at': str(self.created_at) if self.created_at else None,
            'completed_at': str(self.completed_at) if self.completed_at else None
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
            interview_category=data.get('interview_category', 'Technical'),
            difficulty=data.get('difficulty', 'Intermediate'),
            total_questions=data.get('total_questions', 5),
            current_question_index=data.get('current_question_index', 0),
            overall_score=data.get('overall_score'),
            final_feedback=data.get('final_feedback'),
            strengths_summary=data.get('strengths_summary'),
            weaknesses_summary=data.get('weaknesses_summary'),
            recommendations=data.get('recommendations'),
            status=data.get('status', 'in_progress'),
            created_at=data.get('created_at'),
            completed_at=data.get('completed_at')
        )


class MockInterviewQuestion:
    def __init__(self, id=None, session_id=None, question_order=1, question_category='Technical',
                 question=None, suggested_answer=None, user_answer=None, evaluation_feedback=None,
                 strengths=None, weaknesses=None, relevance_score=None, correctness_score=None,
                 completeness_score=None, clarity_score=None, overall_question_score=None, evaluated_at=None):
        self.id = id
        self.session_id = session_id
        self.question_order = question_order
        self.question_category = question_category
        self.question = question
        self.suggested_answer = suggested_answer
        self.user_answer = user_answer
        self.evaluation_feedback = evaluation_feedback
        self.strengths = strengths
        self.weaknesses = weaknesses
        self.relevance_score = float(relevance_score) if relevance_score is not None else None
        self.correctness_score = float(correctness_score) if correctness_score is not None else None
        self.completeness_score = float(completeness_score) if completeness_score is not None else None
        self.clarity_score = float(clarity_score) if clarity_score is not None else None
        self.overall_question_score = float(overall_question_score) if overall_question_score is not None else None
        self.evaluated_at = evaluated_at

    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'question_order': self.question_order,
            'question_category': self.question_category,
            'question': self.question,
            'suggested_answer': self.suggested_answer,
            'user_answer': self.user_answer,
            'evaluation_feedback': self.evaluation_feedback,
            'strengths': self.strengths,
            'weaknesses': self.weaknesses,
            'relevance_score': self.relevance_score,
            'correctness_score': self.correctness_score,
            'completeness_score': self.completeness_score,
            'clarity_score': self.clarity_score,
            'overall_question_score': self.overall_question_score,
            'evaluated_at': str(self.evaluated_at) if self.evaluated_at else None
        }

    @classmethod
    def from_dict(cls, data):
        if not data:
            return None
        return cls(
            id=data.get('id'),
            session_id=data.get('session_id'),
            question_order=data.get('question_order', 1),
            question_category=data.get('question_category', 'Technical'),
            question=data.get('question'),
            suggested_answer=data.get('suggested_answer'),
            user_answer=data.get('user_answer'),
            evaluation_feedback=data.get('evaluation_feedback'),
            strengths=data.get('strengths'),
            weaknesses=data.get('weaknesses'),
            relevance_score=data.get('relevance_score'),
            correctness_score=data.get('correctness_score'),
            completeness_score=data.get('completeness_score'),
            clarity_score=data.get('clarity_score'),
            overall_question_score=data.get('overall_question_score'),
            evaluated_at=data.get('evaluated_at')
        )
