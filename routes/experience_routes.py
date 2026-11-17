from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from routes.auth_routes import login_required
from dao.company_dao import CompanyDAO
from dao.experience_dao import ExperienceDAO

experience_bp = Blueprint('experience', __name__)

@experience_bp.route('/experiences')
def list_experiences():
    company = request.args.get('company', '').strip()
    role = request.args.get('role', '').strip()
    difficulty = request.args.get('difficulty', '').strip()
    experience_level = request.args.get('experience_level', '').strip()
    search = request.args.get('search', '').strip()
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page

    experiences = ExperienceDAO.get_approved(
        company=company if company else None,
        role=role if role else None,
        difficulty=difficulty if difficulty else None,
        experience_level=experience_level if experience_level else None,
        search=search if search else None,
        limit=per_page,
        offset=offset
    )

    total_count = ExperienceDAO.count_approved(
        company=company if company else None,
        role=role if role else None,
        difficulty=difficulty if difficulty else None,
        experience_level=experience_level if experience_level else None,
        search=search if search else None
    )

    total_pages = (total_count + per_page - 1) // per_page
    companies = CompanyDAO.get_all(limit=100)

    return render_template(
        'experiences.html',
        experiences=experiences,
        companies=companies,
        selected_company=company,
        selected_role=role,
        selected_difficulty=difficulty,
        selected_level=experience_level,
        search_query=search,
        page=page,
        total_pages=total_pages,
        total_count=total_count
    )

@experience_bp.route('/experiences/<int:exp_id>')
def experience_detail(exp_id):
    experience = ExperienceDAO.get_by_id(exp_id)
    if not experience:
        flash("Interview experience not found.", "warning")
        return redirect(url_for('experience.list_experiences'))

    # If not approved, only author or admin can view
    current_uid = session.get('user_id')
    current_aid = session.get('admin_id')
    if experience.approval_status != 'approved':
        if experience.user_id != current_uid and not current_aid:
            flash("This interview experience is currently pending administrator review.", "info")
            return redirect(url_for('experience.list_experiences'))

    # Get related experiences from same company
    related = ExperienceDAO.get_approved(company=experience.company_name, limit=3)
    related = [r for r in related if r.id != experience.id]

    return render_template(
        'experience_detail.html',
        experience=experience,
        related_experiences=related
    )

@experience_bp.route('/experiences/add', methods=['GET', 'POST'])
@login_required
def add_experience():
    user = g.current_user
    companies = CompanyDAO.get_all(limit=200)

    if request.method == 'POST':
        company_name = request.form.get('company_name', '').strip()
        job_role = request.form.get('job_role', '').strip()
        interview_date = request.form.get('interview_date', '')
        interview_type = request.form.get('interview_type', 'Online')
        difficulty = request.form.get('difficulty', 'Medium')
        experience_level = request.form.get('experience_level', 'Fresher')
        interview_rounds = int(request.form.get('interview_rounds', 1))
        technical_questions = request.form.get('technical_questions', '').strip()
        hr_questions = request.form.get('hr_questions', '').strip()
        overall_experience = request.form.get('overall_experience', '').strip()
        preparation_tips = request.form.get('preparation_tips', '').strip()
        result = request.form.get('result', 'Not Disclosed')

        # Validation
        if not company_name or len(company_name) < 2:
            flash("Please enter a valid company name.", "danger")
            return render_template('add_experience.html', companies=companies, form=request.form)

        if not job_role or len(job_role) < 2:
            flash("Please enter a valid job role.", "danger")
            return render_template('add_experience.html', companies=companies, form=request.form)

        if not overall_experience or len(overall_experience) < 20:
            flash("Please provide a detailed overall experience (minimum 20 characters).", "danger")
            return render_template('add_experience.html', companies=companies, form=request.form)

        # Get or create company
        company_id = CompanyDAO.get_or_create(company_name)

        # Create experience with pending approval status
        exp_id = ExperienceDAO.create(
            user_id=user.id,
            company_id=company_id,
            job_role=job_role,
            interview_date=interview_date if interview_date else None,
            interview_type=interview_type,
            difficulty=difficulty,
            experience_level=experience_level,
            interview_rounds=interview_rounds,
            technical_questions=technical_questions,
            hr_questions=hr_questions,
            overall_experience=overall_experience,
            preparation_tips=preparation_tips,
            result=result,
            approval_status='pending'
        )

        flash("Interview experience submitted successfully! It has been submitted for administrator review and will be visible publicly once approved.", "success")
        return redirect(url_for('experience.my_experiences'))

    return render_template('add_experience.html', companies=companies)

@experience_bp.route('/my-experiences')
@login_required
def my_experiences():
    user = g.current_user
    experiences = ExperienceDAO.get_user_experiences(user.id)
    return render_template('my_experiences.html', experiences=experiences)

@experience_bp.route('/experiences/<int:exp_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_experience(exp_id):
    user = g.current_user
    experience = ExperienceDAO.get_by_id(exp_id)
    if not experience or experience.user_id != user.id:
        flash("Experience not found or you do not have permission to edit it.", "danger")
        return redirect(url_for('experience.my_experiences'))

    companies = CompanyDAO.get_all(limit=200)

    if request.method == 'POST':
        company_name = request.form.get('company_name', '').strip()
        job_role = request.form.get('job_role', '').strip()
        interview_date = request.form.get('interview_date', '')
        interview_type = request.form.get('interview_type', 'Online')
        difficulty = request.form.get('difficulty', 'Medium')
        experience_level = request.form.get('experience_level', 'Fresher')
        interview_rounds = int(request.form.get('interview_rounds', 1))
        technical_questions = request.form.get('technical_questions', '').strip()
        hr_questions = request.form.get('hr_questions', '').strip()
        overall_experience = request.form.get('overall_experience', '').strip()
        preparation_tips = request.form.get('preparation_tips', '').strip()
        result = request.form.get('result', 'Not Disclosed')

        if not company_name or not job_role or len(overall_experience) < 20:
            flash("Please ensure all required fields are filled with adequate detail.", "danger")
            return render_template('edit_experience.html', experience=experience, companies=companies)

        company_id = CompanyDAO.get_or_create(company_name)

        ExperienceDAO.update(
            exp_id=exp_id,
            user_id=user.id,
            company_id=company_id,
            job_role=job_role,
            interview_date=interview_date if interview_date else None,
            interview_type=interview_type,
            difficulty=difficulty,
            experience_level=experience_level,
            interview_rounds=interview_rounds,
            technical_questions=technical_questions,
            hr_questions=hr_questions,
            overall_experience=overall_experience,
            preparation_tips=preparation_tips,
            result=result,
            reset_approval=True
        )

        flash("Experience updated successfully! Since it was modified, it is now awaiting administrator re-approval.", "info")
        return redirect(url_for('experience.my_experiences'))

    return render_template('edit_experience.html', experience=experience, companies=companies)

@experience_bp.route('/experiences/<int:exp_id>/delete', methods=['POST'])
@login_required
def delete_experience(exp_id):
    user = g.current_user
    success = ExperienceDAO.delete(exp_id, user_id=user.id)
    if success:
        flash("Interview experience deleted successfully.", "success")
    else:
        flash("Could not delete experience or permission denied.", "danger")
    return redirect(url_for('experience.my_experiences'))
