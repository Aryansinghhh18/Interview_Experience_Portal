from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g, jsonify
from routes.auth_routes import login_required
from dao.company_dao import CompanyDAO
from dao.ai_dao import AIDaO
from services.ai.question_generation_service import QuestionGenerationService

question_generator_bp = Blueprint('question_generator', __name__)

@question_generator_bp.route('/question-generator', methods=['GET', 'POST'])
@login_required
def generate():
    user = g.current_user
    companies = CompanyDAO.get_all(limit=100)
    generated_questions = []

    if request.method == 'POST':
        company_name = request.form.get('company_name', '').strip()
        job_role = request.form.get('job_role', '').strip()
        technical_domain = request.form.get('technical_domain', '').strip()
        difficulty = request.form.get('difficulty', 'Intermediate')
        category = request.form.get('category', 'Technical')
        count = int(request.form.get('count', 5))

        if not company_name or not job_role:
            flash("Please provide company name and job role.", "warning")
            return render_template('question_generator.html', companies=companies)

        # Generate questions
        raw_questions = QuestionGenerationService.generate_questions(
            company_name=company_name,
            job_role=job_role,
            technical_domain=technical_domain if technical_domain else None,
            difficulty=difficulty,
            category=category,
            count=count,
            user_id=user.id
        )

        # Save generated questions into database
        for q in raw_questions:
            qid = AIDaO.save_generated_question(
                user_id=user.id,
                company_name=company_name,
                job_role=job_role,
                technical_domain=technical_domain,
                category=q.get('category', category),
                difficulty=q.get('difficulty', difficulty),
                question=q.get('question'),
                suggested_answer=q.get('suggested_answer'),
                explanation=q.get('explanation'),
                key_concepts=q.get('key_concepts')
            )
            q['id'] = qid
            q['company_name'] = company_name
            q['job_role'] = job_role
            q['is_saved'] = False
            generated_questions.append(q)

        flash(f"Successfully generated {len(generated_questions)} role-tailored practice questions!", "success")
        return render_template(
            'question_generator.html',
            companies=companies,
            questions=generated_questions,
            selected_company=company_name,
            selected_role=job_role,
            selected_domain=technical_domain,
            selected_difficulty=difficulty,
            selected_category=category
        )

    # On GET, show recent questions user generated
    recent_questions = AIDaO.get_user_generated_questions(user.id, limit=6)
    return render_template('question_generator.html', companies=companies, recent_questions=recent_questions)

@question_generator_bp.route('/question-generator/save', methods=['POST'])
@login_required
def save_question():
    user = g.current_user
    question_id = int(request.form.get('question_id'))
    notes = request.form.get('notes', '').strip()

    saved_id = AIDaO.bookmark_question(user.id, question_id, notes=notes if notes else None)
    if saved_id:
        return jsonify({'status': 'success', 'message': 'Question saved to bookmarks!'})
    return jsonify({'status': 'error', 'message': 'Already bookmarked or could not save.'}), 400

@question_generator_bp.route('/question-generator/unsave', methods=['POST'])
@login_required
def unsave_question():
    user = g.current_user
    question_id = int(request.form.get('question_id'))
    success = AIDaO.unbookmark_question(user.id, question_id)
    if success:
        return jsonify({'status': 'success', 'message': 'Question removed from bookmarks.'})
    return jsonify({'status': 'error', 'message': 'Could not remove bookmark.'}), 400

@question_generator_bp.route('/saved-questions')
@login_required
def saved_questions():
    user = g.current_user
    questions = AIDaO.get_saved_questions(user.id, limit=50)
    return render_template('saved_questions.html', questions=questions)
