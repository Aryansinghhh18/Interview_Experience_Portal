from flask import Blueprint, render_template, request, redirect, url_for, session, g
from routes.auth_routes import login_required
from dao.company_dao import CompanyDAO
from dao.ai_dao import AIDaO
from services.ai.smart_search_service import SmartSearchService

smart_search_bp = Blueprint('smart_search', __name__)

@smart_search_bp.route('/smart-search')
def index():
    query = request.args.get('q', '').strip()
    company = request.args.get('company', '').strip()
    role = request.args.get('role', '').strip()
    difficulty = request.args.get('difficulty', '').strip()
    experience_level = request.args.get('experience_level', '').strip()

    current_uid = session.get('user_id')

    # Suggested sample queries
    suggested_queries = [
        "Python developer interviews for freshers with difficult technical rounds",
        "Companies that asked SQL indexing, ACID properties and DBMS questions",
        "Amazon leadership principles and behavioral rounds for backend engineers",
        "Google SDE algorithmic rounds with dynamic programming and trees",
        "Entry level full stack web development interview experiences"
    ]

    # User search history & popular searches
    search_history = AIDaO.get_recent_searches(current_uid, limit=5) if current_uid else []
    popular_searches = AIDaO.get_popular_searches(limit=5)
    companies = CompanyDAO.get_all(limit=100)

    results = []
    if query or company or role or difficulty or experience_level:
        results = SmartSearchService.search(
            query=query,
            company=company if company else None,
            role=role if role else None,
            difficulty=difficulty if difficulty else None,
            level=experience_level if experience_level else None,
            top_k=15,
            user_id=current_uid
        )

    return render_template(
        'smart_search.html',
        query=query,
        results=results,
        companies=companies,
        selected_company=company,
        selected_role=role,
        selected_difficulty=difficulty,
        selected_level=experience_level,
        suggested_queries=suggested_queries,
        search_history=search_history,
        popular_searches=popular_searches
    )
