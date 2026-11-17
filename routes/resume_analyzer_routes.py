import os
import json
import uuid
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from routes.auth_routes import login_required
from config import Config
from dao.ai_dao import AIDaO
from services.ai.resume_analysis_service import ResumeAnalysisService

resume_analyzer_bp = Blueprint('resume_analyzer', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@resume_analyzer_bp.route('/resume-analyzer', methods=['GET', 'POST'])
@login_required
def index():
    user = g.current_user
    past_analyses = AIDaO.get_user_resume_analyses(user.id, limit=5)

    if request.method == 'POST':
        if 'resume_file' not in request.files:
            flash("No file part in upload request.", "danger")
            return redirect(request.url)

        file = request.files['resume_file']
        target_role = request.form.get('target_job_role', '').strip()
        job_description = request.form.get('job_description', '').strip()

        if file.filename == '':
            flash("No file selected for upload.", "warning")
            return redirect(request.url)

        if not target_role:
            flash("Please specify your target job role.", "warning")
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash("Invalid file format. Only PDF and DOCX files are supported.", "danger")
            return redirect(request.url)

        # Secure file saving
        original_name = secure_filename(file.filename)
        unique_prefix = uuid.uuid4().hex[:8]
        saved_filename = f"{user.id}_{unique_prefix}_{original_name}"
        
        # Ensure upload folder exists
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        file_path = Config.UPLOAD_FOLDER / saved_filename
        file.save(str(file_path))

        try:
            # 1. Extract text using PyMuPDF / python-docx
            extracted_text = ResumeAnalysisService.extract_text_from_file(file_path)

            # 2. Run AI Analysis
            analysis = ResumeAnalysisService.analyze_resume(
                resume_text=extracted_text,
                target_job_role=target_role,
                job_description=job_description if job_description else None,
                user_id=user.id
            )

            # 3. Store analysis in DB
            analysis_id = AIDaO.create_resume_analysis(
                user_id=user.id,
                original_filename=original_name,
                target_job_role=target_role,
                job_description=job_description,
                extracted_text_reference=saved_filename,
                skills=json.dumps(analysis.get('skills', [])),
                education_summary=analysis.get('education_summary', ''),
                projects_summary=analysis.get('projects_summary', ''),
                experience_summary=analysis.get('experience_summary', ''),
                strengths=json.dumps(analysis.get('strengths', [])),
                weaknesses=json.dumps(analysis.get('weaknesses', [])),
                missing_skills=json.dumps(analysis.get('missing_skills', [])),
                compatibility_score=analysis.get('compatibility_score', 0.0),
                improvement_suggestions=json.dumps(analysis.get('improvement_suggestions', [])),
                suggested_topics=json.dumps(analysis.get('suggested_topics', []))
            )

            flash("Resume analyzed successfully! Review your compatibility report below.", "success")
            return redirect(url_for('resume_analyzer.view_analysis', analysis_id=analysis_id))

        except Exception as e:
            flash(f"Error processing resume: {str(e)}", "danger")
            if file_path.exists():
                try:
                    os.remove(file_path)
                except Exception:
                    pass
            return redirect(url_for('resume_analyzer.index'))

    return render_template('resume_analyzer.html', past_analyses=past_analyses)

@resume_analyzer_bp.route('/resume-analyzer/<int:analysis_id>')
@login_required
def view_analysis(analysis_id):
    user = g.current_user
    analysis = AIDaO.get_resume_analysis(analysis_id, user_id=user.id)
    if not analysis:
        flash("Resume analysis report not found.", "warning")
        return redirect(url_for('resume_analyzer.index'))

    # Parse JSON list fields for display
    def safe_json_loads(data):
        if not data:
            return []
        try:
            val = json.loads(data)
            return val if isinstance(val, list) else [str(val)]
        except Exception:
            return [data]

    parsed_skills = safe_json_loads(analysis.skills)
    parsed_strengths = safe_json_loads(analysis.strengths)
    parsed_weaknesses = safe_json_loads(analysis.weaknesses)
    parsed_missing = safe_json_loads(analysis.missing_skills)
    parsed_suggestions = safe_json_loads(analysis.improvement_suggestions)
    parsed_topics = safe_json_loads(analysis.suggested_topics)

    return render_template(
        'resume_detail.html',
        analysis=analysis,
        skills=parsed_skills,
        strengths=parsed_strengths,
        weaknesses=parsed_weaknesses,
        missing_skills=parsed_missing,
        improvement_suggestions=parsed_suggestions,
        suggested_topics=parsed_topics
    )

@resume_analyzer_bp.route('/resume-analyzer/<int:analysis_id>/delete', methods=['POST'])
@login_required
def delete_analysis(analysis_id):
    user = g.current_user
    analysis = AIDaO.get_resume_analysis(analysis_id, user_id=user.id)
    if not analysis:
        flash("Analysis not found.", "warning")
        return redirect(url_for('resume_analyzer.my_resumes'))

    # Delete physical file if exists
    if analysis.extracted_text_reference:
        file_path = Config.UPLOAD_FOLDER / analysis.extracted_text_reference
        if file_path.exists():
            try:
                os.remove(file_path)
            except Exception:
                pass

    AIDaO.delete_resume_analysis(analysis_id, user.id)
    flash("Resume analysis and stored document deleted successfully (Privacy Cleaned).", "success")
    return redirect(url_for('resume_analyzer.my_resumes'))

@resume_analyzer_bp.route('/my-resumes')
@login_required
def my_resumes():
    user = g.current_user
    analyses = AIDaO.get_user_resume_analyses(user.id, limit=30)
    return render_template('my_resumes.html', analyses=analyses)
