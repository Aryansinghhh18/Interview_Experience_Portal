from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from routes.auth_routes import login_required
from dao.user_dao import UserDAO
from dao.company_dao import CompanyDAO
from dao.experience_dao import ExperienceDAO
from dao.ai_dao import AIDaO
from models.user import User

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard')
@login_required
def dashboard():
    user = g.current_user
    
    # Aggregate statistics
    total_approved_exp = ExperienceDAO.count_approved()
    total_companies = CompanyDAO.count()
    my_experiences = ExperienceDAO.get_user_experiences(user.id)
    my_exp_count = len(my_experiences)
    mock_interviews_completed = AIDaO.count_user_mock_sessions(user.id)
    
    # Latest mock interview session score
    user_sessions = AIDaO.get_user_mock_sessions(user.id, limit=1)
    latest_score = user_sessions[0].overall_score if user_sessions and user_sessions[0].overall_score else None
    
    # Recent approved experiences
    recent_experiences = ExperienceDAO.get_recent_approved(limit=5)
    
    # User's recent resumes
    recent_resumes = AIDaO.get_user_resume_analyses(user.id, limit=3)

    return render_template(
        'dashboard.html',
        user=user,
        total_approved_exp=total_approved_exp,
        total_companies=total_companies,
        my_exp_count=my_exp_count,
        mock_interviews_completed=mock_interviews_completed,
        latest_score=latest_score,
        recent_experiences=recent_experiences,
        recent_resumes=recent_resumes
    )

@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = g.current_user

    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_profile':
            name = request.form.get('name', '').strip()
            if not name or len(name) < 2:
                flash("Name must be at least 2 characters.", "danger")
            else:
                UserDAO.update_user(user.id, name=name)
                session['user_name'] = name
                flash("Profile updated successfully!", "success")
                return redirect(url_for('user.profile'))
                
        elif action == 'change_password':
            current_pw = request.form.get('current_password', '')
            new_pw = request.form.get('new_password', '')
            confirm_pw = request.form.get('confirm_password', '')

            if not user.check_password(current_pw):
                flash("Current password is incorrect.", "danger")
            elif len(new_pw) < 6:
                flash("New password must be at least 6 characters.", "danger")
            elif new_pw != confirm_pw:
                flash("New passwords do not match.", "danger")
            else:
                new_hash = User.hash_password(new_pw)
                UserDAO.update_user(user.id, password_hash=new_hash)
                flash("Password changed successfully!", "success")
                return redirect(url_for('user.profile'))

    # Load user summary
    my_exp_count = len(ExperienceDAO.get_user_experiences(user.id))
    my_mock_count = AIDaO.count_user_mock_sessions(user.id)
    my_resume_count = len(AIDaO.get_user_resume_analyses(user.id))

    return render_template(
        'profile.html',
        user=user,
        my_exp_count=my_exp_count,
        my_mock_count=my_mock_count,
        my_resume_count=my_resume_count
    )
