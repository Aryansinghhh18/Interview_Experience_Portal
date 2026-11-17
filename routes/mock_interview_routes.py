from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g, jsonify
from routes.auth_routes import login_required
from dao.company_dao import CompanyDAO
from dao.ai_dao import AIDaO
from services.ai.mock_interview_service import MockInterviewService

mock_interview_bp = Blueprint('mock_interview', __name__)

@mock_interview_bp.route('/mock-interview')
@login_required
def setup():
    user = g.current_user
    companies = CompanyDAO.get_all(limit=100)
    past_sessions = AIDaO.get_user_mock_sessions(user.id, limit=5)
    return render_template('mock_interview.html', companies=companies, past_sessions=past_sessions)

@mock_interview_bp.route('/mock-interview/start', methods=['POST'])
@login_required
def start():
    user = g.current_user
    company_name = request.form.get('company_name', '').strip()
    job_role = request.form.get('job_role', '').strip()
    category = request.form.get('category', 'Technical')
    difficulty = request.form.get('difficulty', 'Intermediate')
    total_questions = int(request.form.get('total_questions', 5))

    if not company_name or not job_role:
        flash("Please provide both target company and job role.", "danger")
        return redirect(url_for('mock_interview.setup'))

    # Clamp total questions between 1 and 10
    total_questions = max(1, min(total_questions, 10))

    # 1. Create session record
    session_id = AIDaO.create_mock_session(
        user_id=user.id,
        company_name=company_name,
        job_role=job_role,
        interview_category=category,
        difficulty=difficulty,
        total_questions=total_questions
    )

    # 2. Generate questions from AI service
    generated_questions = MockInterviewService.generate_interview_questions(
        company_name=company_name,
        job_role=job_role,
        category=category,
        difficulty=difficulty,
        count=total_questions,
        user_id=user.id
    )

    # 3. Save questions into DB
    for idx, q in enumerate(generated_questions):
        AIDaO.add_mock_question(
            session_id=session_id,
            question_order=idx + 1,
            question_category=q.get('category', 'Technical'),
            question=q.get('question'),
            suggested_answer=q.get('suggested_answer')
        )

    flash(f"Mock interview initialized! {len(generated_questions)} questions prepared.", "success")
    return redirect(url_for('mock_interview.session_runner', session_id=session_id))

@mock_interview_bp.route('/mock-interview/session/<int:session_id>')
@login_required
def session_runner(session_id):
    user = g.current_user
    mock_session = AIDaO.get_mock_session(session_id, user_id=user.id)
    if not mock_session:
        flash("Mock interview session not found.", "warning")
        return redirect(url_for('mock_interview.setup'))

    questions = AIDaO.get_mock_questions(session_id)
    if not questions:
        flash("No questions found for this session.", "danger")
        return redirect(url_for('mock_interview.setup'))

    # If completed, jump straight to report
    if mock_session.status == 'completed':
        return redirect(url_for('mock_interview.report', session_id=session_id))

    # Determine current question to answer
    current_index = mock_session.current_question_index
    if current_index >= len(questions):
        # All questions answered, generate final report
        return redirect(url_for('mock_interview.finalize_session', session_id=session_id))

    current_q = questions[current_index]

    return render_template(
        'mock_interview_session.html',
        interview_session=mock_session,
        questions=questions,
        current_question=current_q,
        current_index=current_index,
        total_questions=len(questions)
    )

@mock_interview_bp.route('/mock-interview/session/<int:session_id>/answer', methods=['POST'])
@login_required
def submit_answer(session_id):
    user = g.current_user
    mock_session = AIDaO.get_mock_session(session_id, user_id=user.id)
    if not mock_session:
        return jsonify({'error': 'Session not found'}), 404

    question_id = int(request.form.get('question_id'))
    user_answer = request.form.get('user_answer', '').strip()

    question = AIDaO.get_mock_question(question_id)
    if not question or question.session_id != session_id:
        return jsonify({'error': 'Invalid question'}), 400

    # Evaluate using AI service
    eval_result = MockInterviewService.evaluate_answer(
        company_name=mock_session.company_name,
        job_role=mock_session.job_role,
        question=question.question,
        user_answer=user_answer,
        user_id=user.id
    )

    # Persist evaluation
    AIDaO.update_mock_question_evaluation(
        question_id=question_id,
        user_answer=user_answer,
        evaluation_feedback=eval_result.get('feedback'),
        strengths=eval_result.get('strengths'),
        weaknesses=eval_result.get('weaknesses'),
        relevance_score=eval_result.get('relevance_score'),
        correctness_score=eval_result.get('correctness_score'),
        completeness_score=eval_result.get('completeness_score'),
        clarity_score=eval_result.get('clarity_score'),
        overall_question_score=eval_result.get('overall_score')
    )

    # Advance session index
    next_index = mock_session.current_question_index + 1
    AIDaO.update_mock_session_progress(session_id, next_index)

    return jsonify({
        'status': 'success',
        'evaluation': eval_result,
        'next_index': next_index,
        'is_last': next_index >= mock_session.total_questions
    })

@mock_interview_bp.route('/mock-interview/session/<int:session_id>/finalize')
@login_required
def finalize_session(session_id):
    user = g.current_user
    mock_session = AIDaO.get_mock_session(session_id, user_id=user.id)
    if not mock_session:
        flash("Session not found.", "warning")
        return redirect(url_for('mock_interview.setup'))

    questions = AIDaO.get_mock_questions(session_id)
    
    # Generate final comprehensive report
    report_data = MockInterviewService.generate_final_report(mock_session, questions, user_id=user.id)

    AIDaO.complete_mock_session(
        session_id=session_id,
        overall_score=report_data.get('overall_score'),
        final_feedback=report_data.get('final_feedback'),
        strengths_summary=report_data.get('strengths_summary'),
        weaknesses_summary=report_data.get('weaknesses_summary'),
        recommendations=report_data.get('recommendations')
    )

    flash("Mock interview completed! Your comprehensive AI performance report is ready.", "success")
    return redirect(url_for('mock_interview.report', session_id=session_id))

@mock_interview_bp.route('/mock-interview/session/<int:session_id>/report')
@login_required
def report(session_id):
    user = g.current_user
    mock_session = AIDaO.get_mock_session(session_id, user_id=user.id)
    if not mock_session:
        flash("Session not found.", "warning")
        return redirect(url_for('mock_interview.setup'))

    questions = AIDaO.get_mock_questions(session_id)
    return render_template('mock_interview_report.html', interview_session=mock_session, questions=questions)

@mock_interview_bp.route('/mock-interview/history')
@login_required
def history():
    user = g.current_user
    sessions = AIDaO.get_user_mock_sessions(user.id, limit=50)
    return render_template('mock_interview_history.html', sessions=sessions)
