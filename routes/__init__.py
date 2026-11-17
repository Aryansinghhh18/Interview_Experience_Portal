from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.experience_routes import experience_bp
from routes.admin_routes import admin_bp
from routes.mock_interview_routes import mock_interview_bp
from routes.question_generator_routes import question_generator_bp
from routes.resume_analyzer_routes import resume_analyzer_bp
from routes.smart_search_routes import smart_search_bp
from routes.performance_routes import performance_bp

__all__ = [
    'auth_bp',
    'user_bp',
    'experience_bp',
    'admin_bp',
    'mock_interview_bp',
    'question_generator_bp',
    'resume_analyzer_bp',
    'smart_search_bp',
    'performance_bp'
]
