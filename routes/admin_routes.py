from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from routes.auth_routes import admin_required
from dao.user_dao import UserDAO, AdminDAO
from dao.company_dao import CompanyDAO
from dao.experience_dao import ExperienceDAO
from dao.ai_dao import AIDaO
from database import query_one, query_all
from config import Config

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('admin_id'):
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        username_or_email = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        admin = AdminDAO.get_by_username(username_or_email) or AdminDAO.get_by_email(username_or_email)
        if not admin or not admin.check_password(password):
            flash("Invalid administrator credentials.", "danger")
            return render_template('admin_login.html', username=username_or_email)

        if not admin.is_active:
            flash("Administrator account is inactive.", "danger")
            return render_template('admin_login.html', username=username_or_email)

        session.clear()
        session['admin_id'] = admin.id
        session['admin_username'] = admin.username
        session['admin_email'] = admin.email
        session['is_admin'] = True

        AIDaO.log_admin_audit(admin.id, "LOGIN", "admin", admin.id, "Admin logged in successfully", request.remote_addr)
        flash(f"Welcome to Admin Portal, {admin.username}!", "success")
        return redirect(url_for('admin.dashboard'))

    return render_template('admin_login.html')

@admin_bp.route('/logout')
def logout():
    aid = session.get('admin_id')
    if aid:
        AIDaO.log_admin_audit(aid, "LOGOUT", "admin", aid, "Admin logged out", request.remote_addr)
    session.clear()
    flash("Admin logged out successfully.", "info")
    return redirect(url_for('admin.login'))

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    aid = session.get('admin_id')

    # Aggregate metrics
    total_users = UserDAO.count_users()
    exp_stats = ExperienceDAO.get_stats()
    total_companies = CompanyDAO.count()
    
    # Mock interview and resume counts
    res_mock = query_one("SELECT COUNT(*) as c FROM mock_interview_sessions")
    total_mocks = res_mock['c'] if res_mock else 0

    res_resumes = query_one("SELECT COUNT(*) as c FROM resume_analyses")
    total_resumes = res_resumes['c'] if res_resumes else 0

    ai_stats = AIDaO.get_ai_usage_stats()
    recent_audits = AIDaO.get_admin_audit_logs(limit=8)
    pending_experiences = ExperienceDAO.get_all_admin(status='pending', limit=5)

    return render_template(
        'admin_dashboard.html',
        total_users=total_users,
        exp_stats=exp_stats,
        total_companies=total_companies,
        total_mocks=total_mocks,
        total_resumes=total_resumes,
        ai_stats=ai_stats,
        recent_audits=recent_audits,
        pending_experiences=pending_experiences,
        active_provider=Config.AI_PROVIDER
    )

@admin_bp.route('/users', methods=['GET', 'POST'])
@admin_required
def users():
    aid = session.get('admin_id')
    search = request.args.get('search', '').strip()
    page = int(request.args.get('page', 1))
    per_page = 20
    offset = (page - 1) * per_page

    if request.method == 'POST':
        action = request.form.get('action')
        target_uid = int(request.form.get('user_id'))
        target_user = UserDAO.get_by_id(target_uid)

        if action == 'toggle_status':
            new_status = not target_user.is_active
            UserDAO.update_user(target_uid, is_active=new_status)
            status_text = "activated" if new_status else "deactivated"
            AIDaO.log_admin_audit(aid, "USER_STATUS_CHANGE", "user", target_uid, f"User {status_text}", request.remote_addr)
            flash(f"User account {status_text}.", "success")
        elif action == 'delete_user':
            UserDAO.delete_user(target_uid)
            AIDaO.log_admin_audit(aid, "USER_DELETE", "user", target_uid, f"User {target_user.email} deleted", request.remote_addr)
            flash("User account deleted successfully.", "success")

        return redirect(url_for('admin.users', search=search, page=page))

    users_list = UserDAO.get_all(search=search if search else None, limit=per_page, offset=offset)
    total_users = UserDAO.count_users(search=search if search else None)
    total_pages = (total_users + per_page - 1) // per_page

    return render_template(
        'admin_users.html',
        users=users_list,
        search=search,
        page=page,
        total_pages=total_pages,
        total_users=total_users
    )

@admin_bp.route('/experiences', methods=['GET', 'POST'])
@admin_required
def experiences():
    aid = session.get('admin_id')
    status = request.args.get('status', '').strip()
    search = request.args.get('search', '').strip()
    page = int(request.args.get('page', 1))
    per_page = 20
    offset = (page - 1) * per_page

    if request.method == 'POST':
        action = request.form.get('action')
        exp_id = int(request.form.get('experience_id'))

        if action == 'approve':
            ExperienceDAO.update_approval(exp_id, 'approved')
            AIDaO.log_admin_audit(aid, "EXPERIENCE_APPROVE", "experience", exp_id, "Experience approved for public view", request.remote_addr)
            flash("Experience approved successfully and is now live!", "success")
        elif action == 'reject':
            reason = request.form.get('rejection_reason', 'Did not meet submission guidelines.')
            ExperienceDAO.update_approval(exp_id, 'rejected', rejection_reason=reason)
            AIDaO.log_admin_audit(aid, "EXPERIENCE_REJECT", "experience", exp_id, f"Reason: {reason}", request.remote_addr)
            flash("Experience rejected.", "info")
        elif action == 'delete':
            ExperienceDAO.delete(exp_id)
            AIDaO.log_admin_audit(aid, "EXPERIENCE_DELETE", "experience", exp_id, "Experience deleted by admin", request.remote_addr)
            flash("Experience deleted permanently.", "success")

        return redirect(url_for('admin.experiences', status=status, search=search, page=page))

    experiences_list = ExperienceDAO.get_all_admin(
        status=status if status else None,
        search=search if search else None,
        limit=per_page,
        offset=offset
    )
    total_count = ExperienceDAO.count_all_admin(
        status=status if status else None,
        search=search if search else None
    )
    total_pages = (total_count + per_page - 1) // per_page

    return render_template(
        'admin_experiences.html',
        experiences=experiences_list,
        current_status=status,
        search=search,
        page=page,
        total_pages=total_pages,
        total_count=total_count
    )

@admin_bp.route('/companies', methods=['GET', 'POST'])
@admin_required
def companies():
    aid = session.get('admin_id')
    search = request.args.get('search', '').strip()

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create':
            name = request.form.get('company_name', '').strip()
            desc = request.form.get('description', '').strip()
            web = request.form.get('website', '').strip()
            if name:
                try:
                    cid = CompanyDAO.create(name, desc, web)
                    AIDaO.log_admin_audit(aid, "COMPANY_CREATE", "company", cid, f"Created {name}", request.remote_addr)
                    flash(f"Company '{name}' added successfully.", "success")
                except Exception as e:
                    flash(f"Error creating company: {e}", "danger")
        elif action == 'update':
            cid = int(request.form.get('company_id'))
            name = request.form.get('company_name', '').strip()
            desc = request.form.get('description', '').strip()
            web = request.form.get('website', '').strip()
            try:
                CompanyDAO.update(cid, name, desc, web)
                AIDaO.log_admin_audit(aid, "COMPANY_UPDATE", "company", cid, f"Updated {name}", request.remote_addr)
                flash(f"Company '{name}' updated successfully.", "success")
            except Exception as e:
                flash(f"Error updating company: {e}", "danger")
        elif action == 'delete':
            cid = int(request.form.get('company_id'))
            try:
                CompanyDAO.delete(cid)
                AIDaO.log_admin_audit(aid, "COMPANY_DELETE", "company", cid, f"Deleted company ID {cid}", request.remote_addr)
                flash("Company deleted successfully.", "success")
            except Exception as e:
                flash(f"Error deleting company: {e}", "danger")

        return redirect(url_for('admin.companies', search=search))

    companies_list = CompanyDAO.get_all(search=search if search else None, limit=100)
    return render_template('admin_companies.html', companies=companies_list, search=search)

@admin_bp.route('/ai-usage')
@admin_required
def ai_usage():
    stats = AIDaO.get_ai_usage_stats()
    logs = AIDaO.get_ai_usage_logs(limit=50)
    return render_template(
        'admin_ai_usage.html',
        stats=stats,
        logs=logs,
        current_provider=Config.AI_PROVIDER,
        gemini_model=Config.GEMINI_MODEL,
        openai_model=Config.OPENAI_MODEL,
        has_gemini_key=bool(Config.GEMINI_API_KEY and "your_gemini" not in Config.GEMINI_API_KEY),
        has_openai_key=bool(Config.OPENAI_API_KEY and "your_openai" not in Config.OPENAI_API_KEY)
    )

@admin_bp.route('/reports')
@admin_required
def reports():
    exp_stats = ExperienceDAO.get_stats()
    popular_companies = CompanyDAO.get_popular(limit=8)
    popular_searches = AIDaO.get_popular_searches(limit=8)
    ai_stats = AIDaO.get_ai_usage_stats()
    
    # Recent activity
    recent_audits = AIDaO.get_admin_audit_logs(limit=30)

    return render_template(
        'admin_reports.html',
        exp_stats=exp_stats,
        popular_companies=popular_companies,
        popular_searches=popular_searches,
        ai_stats=ai_stats,
        recent_audits=recent_audits
    )
