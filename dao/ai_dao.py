from datetime import datetime
from database import query_one, query_all, execute_insert, execute
from models.mock_interview import MockInterviewSession, MockInterviewQuestion
from models.resume_analysis import ResumeAnalysis, GeneratedQuestion

class AIDaO:
    # -------------------------------------------------------------
    # Mock Interview Operations
    # -------------------------------------------------------------
    @staticmethod
    def create_mock_session(user_id, company_name, job_role, interview_category, difficulty, total_questions):
        sql = """
        INSERT INTO mock_interview_sessions (
            user_id, company_name, job_role, interview_category, difficulty, total_questions, status
        ) VALUES (%s, %s, %s, %s, %s, %s, 'in_progress')
        """
        return execute_insert(sql, (user_id, company_name.strip(), job_role.strip(), interview_category, difficulty, total_questions))

    @staticmethod
    def get_mock_session(session_id, user_id=None):
        if user_id:
            sql = "SELECT * FROM mock_interview_sessions WHERE id = %s AND user_id = %s"
            row = query_one(sql, (session_id, user_id))
        else:
            sql = "SELECT * FROM mock_interview_sessions WHERE id = %s"
            row = query_one(sql, (session_id,))
        return MockInterviewSession.from_dict(row) if row else None

    @staticmethod
    def add_mock_question(session_id, question_order, question_category, question, suggested_answer):
        sql = """
        INSERT INTO mock_interview_questions (
            session_id, question_order, question_category, question, suggested_answer
        ) VALUES (%s, %s, %s, %s, %s)
        """
        return execute_insert(sql, (session_id, question_order, question_category, question, suggested_answer))

    @staticmethod
    def get_mock_questions(session_id):
        sql = """
        SELECT * FROM mock_interview_questions 
        WHERE session_id = %s 
        ORDER BY question_order ASC
        """
        rows = query_all(sql, (session_id,))
        return [MockInterviewQuestion.from_dict(r) for r in rows]

    @staticmethod
    def get_mock_question(question_id):
        sql = "SELECT * FROM mock_interview_questions WHERE id = %s"
        row = query_one(sql, (question_id,))
        return MockInterviewQuestion.from_dict(row) if row else None

    @staticmethod
    def update_mock_question_evaluation(question_id, user_answer, evaluation_feedback,
                                        strengths, weaknesses, relevance_score,
                                        correctness_score, completeness_score,
                                        clarity_score, overall_question_score):
        sql = """
        UPDATE mock_interview_questions 
        SET user_answer = %s, evaluation_feedback = %s, strengths = %s, weaknesses = %s,
            relevance_score = %s, correctness_score = %s, completeness_score = %s,
            clarity_score = %s, overall_question_score = %s, evaluated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        """
        return execute(sql, (
            user_answer, evaluation_feedback, strengths, weaknesses,
            relevance_score, correctness_score, completeness_score,
            clarity_score, overall_question_score, question_id
        )) > 0

    @staticmethod
    def update_mock_session_progress(session_id, current_index):
        sql = "UPDATE mock_interview_sessions SET current_question_index = %s WHERE id = %s"
        return execute(sql, (current_index, session_id)) > 0

    @staticmethod
    def complete_mock_session(session_id, overall_score, final_feedback,
                               strengths_summary, weaknesses_summary, recommendations):
        sql = """
        UPDATE mock_interview_sessions 
        SET overall_score = %s, final_feedback = %s, strengths_summary = %s,
            weaknesses_summary = %s, recommendations = %s, status = 'completed',
            completed_at = CURRENT_TIMESTAMP
        WHERE id = %s
        """
        return execute(sql, (
            overall_score, final_feedback, strengths_summary,
            weaknesses_summary, recommendations, session_id
        )) > 0

    @staticmethod
    def get_user_mock_sessions(user_id, limit=20):
        sql = """
        SELECT * FROM mock_interview_sessions 
        WHERE user_id = %s 
        ORDER BY created_at DESC 
        LIMIT %s
        """
        rows = query_all(sql, (user_id, limit))
        return [MockInterviewSession.from_dict(r) for r in rows]

    @staticmethod
    def count_user_mock_sessions(user_id):
        sql = "SELECT COUNT(*) as c FROM mock_interview_sessions WHERE user_id = %s AND status = 'completed'"
        row = query_one(sql, (user_id,))
        return row['c'] if row else 0

    # -------------------------------------------------------------
    # Generated & Saved Questions
    # -------------------------------------------------------------
    @staticmethod
    def save_generated_question(user_id, company_name, job_role, technical_domain,
                                category, difficulty, question, suggested_answer,
                                explanation, key_concepts):
        sql = """
        INSERT INTO generated_questions (
            user_id, company_name, job_role, technical_domain, category, difficulty,
            question, suggested_answer, explanation, key_concepts
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        return execute_insert(sql, (
            user_id, company_name.strip(), job_role.strip(),
            technical_domain.strip() if technical_domain else None,
            category, difficulty, question, suggested_answer, explanation, key_concepts
        ))

    @staticmethod
    def bookmark_question(user_id, generated_question_id, notes=None):
        sql = """
        INSERT INTO saved_questions (user_id, generated_question_id, notes)
        VALUES (%s, %s, %s)
        """
        try:
            return execute_insert(sql, (user_id, generated_question_id, notes))
        except Exception:
            return None

    @staticmethod
    def unbookmark_question(user_id, generated_question_id):
        sql = "DELETE FROM saved_questions WHERE user_id = %s AND generated_question_id = %s"
        return execute(sql, (user_id, generated_question_id)) > 0

    @staticmethod
    def get_saved_questions(user_id, limit=50):
        sql = """
        SELECT q.*, s.notes, s.created_at as saved_at, 1 as is_saved
        FROM saved_questions s
        JOIN generated_questions q ON s.generated_question_id = q.id
        WHERE s.user_id = %s
        ORDER BY s.created_at DESC
        LIMIT %s
        """
        rows = query_all(sql, (user_id, limit))
        return [GeneratedQuestion.from_dict(r) for r in rows]

    @staticmethod
    def get_user_generated_questions(user_id, limit=30):
        sql = """
        SELECT q.*, (CASE WHEN s.id IS NOT NULL THEN 1 ELSE 0 END) as is_saved
        FROM generated_questions q
        LEFT JOIN saved_questions s ON q.id = s.generated_question_id AND s.user_id = %s
        WHERE q.user_id = %s
        ORDER BY q.created_at DESC
        LIMIT %s
        """
        rows = query_all(sql, (user_id, user_id, limit))
        return [GeneratedQuestion.from_dict(r) for r in rows]

    # -------------------------------------------------------------
    # Resume Analyses
    # -------------------------------------------------------------
    @staticmethod
    def create_resume_analysis(user_id, original_filename, target_job_role,
                               job_description, extracted_text_reference, skills,
                               education_summary, projects_summary, experience_summary,
                               strengths, weaknesses, missing_skills, compatibility_score,
                               improvement_suggestions, suggested_topics):
        sql = """
        INSERT INTO resume_analyses (
            user_id, original_filename, target_job_role, job_description,
            extracted_text_reference, skills, education_summary, projects_summary,
            experience_summary, strengths, weaknesses, missing_skills,
            compatibility_score, improvement_suggestions, suggested_topics
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        return execute_insert(sql, (
            user_id, original_filename, target_job_role, job_description,
            extracted_text_reference, skills, education_summary, projects_summary,
            experience_summary, strengths, weaknesses, missing_skills,
            compatibility_score, improvement_suggestions, suggested_topics
        ))

    @staticmethod
    def get_resume_analysis(analysis_id, user_id=None):
        if user_id:
            sql = "SELECT * FROM resume_analyses WHERE id = %s AND user_id = %s"
            row = query_one(sql, (analysis_id, user_id))
        else:
            sql = "SELECT * FROM resume_analyses WHERE id = %s"
            row = query_one(sql, (analysis_id,))
        return ResumeAnalysis.from_dict(row) if row else None

    @staticmethod
    def get_user_resume_analyses(user_id, limit=20):
        sql = """
        SELECT * FROM resume_analyses 
        WHERE user_id = %s 
        ORDER BY created_at DESC 
        LIMIT %s
        """
        rows = query_all(sql, (user_id, limit))
        return [ResumeAnalysis.from_dict(r) for r in rows]

    @staticmethod
    def delete_resume_analysis(analysis_id, user_id):
        sql = "DELETE FROM resume_analyses WHERE id = %s AND user_id = %s"
        return execute(sql, (analysis_id, user_id)) > 0

    # -------------------------------------------------------------
    # AI Usage & Audit Logging
    # -------------------------------------------------------------
    @staticmethod
    def log_ai_usage(user_id, feature_name, provider, model_name, status='success',
                     prompt_tokens=0, completion_tokens=0, token_usage=0,
                     estimated_cost=0.0, error_message=None):
        sql = """
        INSERT INTO ai_usage_logs (
            user_id, feature_name, provider, model_name, status,
            prompt_tokens, completion_tokens, token_usage, estimated_cost, error_message
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        return execute_insert(sql, (
            user_id, feature_name, provider, model_name, status,
            prompt_tokens, completion_tokens, token_usage, estimated_cost, error_message
        ))

    @staticmethod
    def get_ai_usage_stats():
        sql = """
        SELECT 
            COUNT(*) as total_requests,
            SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful_requests,
            SUM(CASE WHEN status != 'success' THEN 1 ELSE 0 END) as failed_requests,
            SUM(token_usage) as total_tokens,
            SUM(estimated_cost) as total_cost
        FROM ai_usage_logs
        """
        row = query_one(sql)
        
        # Feature breakdown
        sql_features = """
        SELECT feature_name, COUNT(*) as count, SUM(token_usage) as tokens
        FROM ai_usage_logs
        GROUP BY feature_name
        ORDER BY count DESC
        """
        feature_breakdown = query_all(sql_features)

        # Provider breakdown
        sql_providers = """
        SELECT provider, COUNT(*) as count, SUM(token_usage) as tokens
        FROM ai_usage_logs
        GROUP BY provider
        """
        provider_breakdown = query_all(sql_providers)

        return {
            'total_requests': row['total_requests'] if row and row['total_requests'] else 0,
            'successful_requests': row['successful_requests'] if row and row['successful_requests'] else 0,
            'failed_requests': row['failed_requests'] if row and row['failed_requests'] else 0,
            'total_tokens': row['total_tokens'] if row and row['total_tokens'] else 0,
            'total_cost': float(row['total_cost']) if row and row['total_cost'] else 0.0,
            'feature_breakdown': feature_breakdown,
            'provider_breakdown': provider_breakdown
        }

    @staticmethod
    def get_ai_usage_logs(limit=50, offset=0):
        sql = """
        SELECT l.*, u.name as user_name, u.email as user_email
        FROM ai_usage_logs l
        LEFT JOIN users u ON l.user_id = u.id
        ORDER BY l.created_at DESC
        LIMIT %s OFFSET %s
        """
        return query_all(sql, (limit, offset))

    @staticmethod
    def log_admin_audit(admin_id, action, target_type, target_id=None, details=None, ip_address=None):
        sql = """
        INSERT INTO admin_audit_logs (
            admin_id, action, target_type, target_id, details, ip_address
        ) VALUES (%s, %s, %s, %s, %s, %s)
        """
        return execute_insert(sql, (admin_id, action, target_type, target_id, details, ip_address))

    @staticmethod
    def get_admin_audit_logs(limit=50, offset=0):
        sql = """
        SELECT a.*, adm.username as admin_username
        FROM admin_audit_logs a
        LEFT JOIN admins adm ON a.admin_id = adm.id
        ORDER BY a.created_at DESC
        LIMIT %s OFFSET %s
        """
        return query_all(sql, (limit, offset))

    # -------------------------------------------------------------
    # Search History
    # -------------------------------------------------------------
    @staticmethod
    def log_search(user_id, search_query, results_count=0):
        sql = "INSERT INTO search_history (user_id, search_query, results_count) VALUES (%s, %s, %s)"
        return execute_insert(sql, (user_id, search_query.strip(), results_count))

    @staticmethod
    def get_recent_searches(user_id, limit=5):
        if not user_id:
            return []
        sql = "SELECT DISTINCT search_query FROM search_history WHERE user_id = %s ORDER BY id DESC LIMIT %s"
        rows = query_all(sql, (user_id, limit))
        return [r['search_query'] for r in rows]

    @staticmethod
    def get_popular_searches(limit=5):
        sql = """
        SELECT search_query, COUNT(*) as count 
        FROM search_history 
        GROUP BY search_query 
        ORDER BY count DESC 
        LIMIT %s
        """
        rows = query_all(sql, (limit,))
        return [r['search_query'] for r in rows]
