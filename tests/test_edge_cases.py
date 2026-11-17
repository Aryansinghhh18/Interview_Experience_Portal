import io
import pytest
from services.ai.gemini_provider import GeminiProvider
from services.ai.openai_provider import OpenAIProvider
from services.ai.mock_interview_service import MockInterviewService
from services.ai.resume_analysis_service import ResumeAnalysisService
from services.ai.smart_search_service import SmartSearchService
from services.ai.performance_analysis_service import PerformanceAnalysisService

def test_unconfigured_gemini_provider():
    provider = GeminiProvider(api_key="")
    assert provider.is_configured() is False
    res = provider.generate_text("Hello test")
    assert res['status'] == 'error'
    assert "not configured" in res['error'].lower()

def test_unconfigured_openai_provider():
    provider = OpenAIProvider(api_key="")
    assert provider.is_configured() is False
    res = provider.generate_text("Hello test")
    assert res['status'] == 'error'
    assert "not configured" in res['error'].lower()

def test_mock_interview_empty_answer():
    eval_res = MockInterviewService.evaluate_answer(
        company_name="Google",
        job_role="SDE",
        question="What is an inverted index?",
        user_answer=""
    )
    assert eval_res['overall_score'] <= 25.0
    assert "brief or empty" in eval_res['weaknesses']

def test_resume_analyzer_unsupported_file(auth_client):
    data = {
        'target_job_role': 'Frontend Developer',
        'resume_file': (io.BytesIO(b"fake image bytes"), 'malicious.exe')
    }
    res = auth_client.post('/resume-analyzer', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert b"Invalid file format" in res.data

def test_performance_analysis_empty_state_user():
    # User ID with 0 interviews
    analytics = PerformanceAnalysisService.get_user_performance_analytics(999999)
    assert analytics['has_data'] is False
    assert analytics['total_interviews'] == 0
    assert analytics['average_score'] == 0.0
    assert "have not completed any mock interviews" in analytics['ai_recommendations']

def test_smart_search_empty_query():
    results = SmartSearchService.search("")
    assert isinstance(results, list)
