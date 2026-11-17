import json
from flask import Blueprint, render_template, request, session, g
from routes.auth_routes import login_required
from services.ai.performance_analysis_service import PerformanceAnalysisService

performance_bp = Blueprint('performance', __name__)

@performance_bp.route('/performance-analysis')
@login_required
def index():
    user = g.current_user
    analytics = PerformanceAnalysisService.get_user_performance_analytics(user.id)

    # Encode chart JSON strings for safe rendering in Jinja templates
    timeline_labels_json = json.dumps(analytics.get('timeline_labels', []))
    timeline_scores_json = json.dumps(analytics.get('timeline_scores', []))
    category_labels_json = json.dumps(analytics.get('category_labels', []))
    category_scores_json = json.dumps(analytics.get('category_scores', []))

    return render_template(
        'performance_analysis.html',
        analytics=analytics,
        timeline_labels_json=timeline_labels_json,
        timeline_scores_json=timeline_scores_json,
        category_labels_json=category_labels_json,
        category_scores_json=category_scores_json
    )
