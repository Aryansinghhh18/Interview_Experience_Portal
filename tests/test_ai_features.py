import io
import json
import pytest
from pathlib import Path
from services.ai.mock_interview_service import MockInterviewService
from services.ai.question_generation_service import QuestionGenerationService
from services.ai.resume_analysis_service import ResumeAnalysisService
from services.ai.smart_search_service import SmartSearchService
from services.ai.performance_analysis_service import PerformanceAnalysisService
from dao.ai_dao import AIDaO
from dao.company_dao import CompanyDAO
from dao.experience_dao import ExperienceDAO

def test_mock_interview_question_generation():
    questions = MockInterviewService.generate_interview_questions(
        company_name="Google",
        job_role="Software Engineer",
        category="Technical",
        difficulty="Intermediate",
        count=3
    )
    assert len(questions) >= 1
    assert "question" in questions[0]
    assert "suggested_answer" in questions[0]

def test_mock_interview_answer_evaluation():
    eval_res = MockInterviewService.evaluate_answer(
        company_name="Amazon",
        job_role="Backend Developer",
        question="How does database indexing improve query performance?",
        user_answer="Database indexes use data structures like B-Trees to avoid full table scans, reducing query lookup time to O(log N)."
    )
    assert "relevance_score" in eval_res
    assert "correctness_score" in eval_res
    assert "completeness_score" in eval_res
    assert "clarity_score" in eval_res
    assert "overall_score" in eval_res
    assert eval_res['overall_score'] >= 0.0

def test_mock_interview_full_flow(auth_client, user_account):
    # 1. Start mock interview
    res = auth_client.post('/mock-interview/start', data={
        'company_name': 'Microsoft',
        'job_role': 'Full Stack Engineer',
        'category': 'Technical',
        'difficulty': 'Intermediate',
        'total_questions': 2
    }, follow_redirects=False)

    assert res.status_code == 302
    session_url = res.location
    session_id = int(session_url.split('/')[-1])

    session_obj = AIDaO.get_mock_session(session_id)
    assert session_obj is not None
    assert session_obj.status == 'in_progress'

    # Get questions
    questions = AIDaO.get_mock_questions(session_id)
    assert len(questions) >= 1

    # 2. Answer question 1
    q1 = questions[0]
    ans_res = auth_client.post(f'/mock-interview/session/{session_id}/answer', data={
        'question_id': q1.id,
        'user_answer': 'I approach web architecture using modular REST APIs with clear separation between data access and presentation layers.'
    })
    assert ans_res.status_code == 200
    ans_json = ans_res.get_json()
    assert ans_json['status'] == 'success'
    assert 'evaluation' in ans_json

    # 3. Finalize session
    fin_res = auth_client.get(f'/mock-interview/session/{session_id}/finalize', follow_redirects=True)
    assert fin_res.status_code == 200
    assert b"Comprehensive Interview Performance Report" in fin_res.data

    completed_session = AIDaO.get_mock_session(session_id)
    assert completed_session.status == 'completed'
    assert completed_session.overall_score is not None

def test_question_generator_flow(auth_client, user_account):
    res = auth_client.post('/question-generator', data={
        'company_name': 'Uber',
        'job_role': 'Distributed Systems Engineer',
        'technical_domain': 'Golang & Microservices',
        'category': 'Technical',
        'difficulty': 'Intermediate',
        'count': 2
    }, follow_redirects=True)

    assert res.status_code == 200
    assert b"Generated Practice Questions" in res.data or b"practice questions" in res.data

def test_question_bookmark_and_unsave(auth_client, user_account):
    # Save a question
    qid = AIDaO.save_generated_question(
        user_id=user_account.id,
        company_name="Apple",
        job_role="iOS Engineer",
        technical_domain="Swift",
        category="Technical",
        difficulty="Intermediate",
        question="Explain ARC and weak references in Swift.",
        suggested_answer="ARC automatically tracks and manages app memory.",
        explanation="Crucial for preventing retain cycles.",
        key_concepts="ARC, Memory Management, Weak References"
    )

    # Bookmark
    save_res = auth_client.post('/question-generator/save', data={'question_id': qid})
    assert save_res.status_code == 200
    assert save_res.get_json()['status'] == 'success'

    # Check saved questions page
    saved_page = auth_client.get('/saved-questions')
    assert b"Explain ARC and weak references" in saved_page.data

    # Unsave
    unsave_res = auth_client.post('/question-generator/unsave', data={'question_id': qid})
    assert unsave_res.status_code == 200
    assert unsave_res.get_json()['status'] == 'success'

def test_resume_upload_and_analysis(auth_client, user_account):
    # Create real in-memory PDF using PyMuPDF
    import pymupdf
    pdf_doc = pymupdf.open()
    page = pdf_doc.new_page()
    page.insert_text((50, 72), "John Doe\nSoftware Engineer\nSkills: Python, Flask, SQL, Docker, Git, REST APIs\nEducation: B.Tech Computer Science\nProjects: Built full-stack e-commerce API platform with MySQL.")
    pdf_bytes = pdf_doc.write()
    pdf_doc.close()

    data = {
        'target_job_role': 'Python Backend Developer',
        'job_description': 'Seeking an experienced Python developer skilled in Flask, MySQL, and Docker.',
        'resume_file': (io.BytesIO(pdf_bytes), 'test_resume.pdf')
    }

    res = auth_client.post('/resume-analyzer', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert res.status_code == 200
    assert b"Compatibility" in res.data or b"Resume" in res.data

def test_smart_search_retrieval(client):
    res = client.get('/smart-search?q=Python+developer+interviews')
    assert res.status_code == 200
    assert b"Smart Search" in res.data

def test_performance_analysis_dashboard(auth_client):
    res = auth_client.get('/performance-analysis')
    assert res.status_code == 200
    assert b"Performance" in res.data
