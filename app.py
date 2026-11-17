import os
import sys
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, session, g
from flask_wtf.csrf import CSRFProtect

# Ensure current folder is in Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from config import Config
from database import close_db, init_db
from routes import (
    auth_bp,
    user_bp,
    experience_bp,
    admin_bp,
    mock_interview_bp,
    question_generator_bp,
    resume_analyzer_bp,
    smart_search_bp,
    performance_bp
)
from dao.company_dao import CompanyDAO
from dao.experience_dao import ExperienceDAO
from dao.user_dao import UserDAO

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize CSRF Protection
    csrf = CSRFProtect(app)
    
    # Exempt API json submission routes from CSRF if needed or pass CSRF header
    # Let's exempt the mock interview ajax submission and question bookmarking ajax
    # or handle via meta tag headers in JavaScript.
    # Note: Flask-WTF verifies X-CSRFToken headers automatically when provided in JS.

    # Teardown database connections
    app.teardown_appcontext(close_db)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(experience_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(mock_interview_bp)
    app.register_blueprint(question_generator_bp)
    app.register_blueprint(resume_analyzer_bp)
    app.register_blueprint(smart_search_bp)
    app.register_blueprint(performance_bp)

    # Global Template Context
    @app.context_processor
    def inject_global_vars():
        return {
            'current_year': datetime.now().year,
            'active_ai_provider': Config.AI_PROVIDER,
            'current_user': g.get('current_user', None),
            'current_admin': g.get('current_admin', None)
        }

    # Public Landing Page
    @app.route('/')
    def index():
        if session.get('user_id'):
            # If already logged in, show user dashboard
            return render_template('index.html', 
                                   stats=ExperienceDAO.get_stats(),
                                   popular_companies=CompanyDAO.get_popular(limit=6),
                                   recent_experiences=ExperienceDAO.get_recent_approved(limit=6),
                                   total_companies=CompanyDAO.count(),
                                   total_experiences=ExperienceDAO.count_approved())

        return render_template(
            'index.html',
            stats=ExperienceDAO.get_stats(),
            popular_companies=CompanyDAO.get_popular(limit=6),
            recent_experiences=ExperienceDAO.get_recent_approved(limit=6),
            total_companies=CompanyDAO.count(),
            total_experiences=ExperienceDAO.count_approved()
        )

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', error_title="404 - Page Not Found", 
                               error_msg="The page you requested could not be found."), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('base.html', error_title="403 - Forbidden", 
                               error_msg="You do not have permission to view this resource."), 403

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('base.html', error_title="500 - Server Error", 
                               error_msg="An internal server error occurred. Please try again later."), 500

    @app.errorhandler(413)
    def file_too_large(e):
        return render_template('base.html', error_title="413 - File Too Large", 
                               error_msg="The uploaded file exceeds the 10MB maximum size limit."), 413

    return app

if __name__ == '__main__':
    # Initialize DB tables on startup
    init_db()
    app = create_app()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
