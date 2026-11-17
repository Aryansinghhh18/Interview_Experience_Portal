import logging
from typing import Dict, Any, List, Optional
from database import query_all, query_one
from services.ai.ai_factory import AIFactory
from dao.ai_dao import AIDaO

logger = logging.getLogger(__name__)

class PerformanceAnalysisService:
    @staticmethod
    def get_user_performance_analytics(user_id: int) -> Dict[str, Any]:
        """
        Aggregate real mock interview data for a user to power the analytics dashboard.
        """
        # Fetch completed sessions
        sql_sessions = """
        SELECT * FROM mock_interview_sessions
        WHERE user_id = %s AND status = 'completed'
        ORDER BY created_at ASC
        """
        sessions = query_all(sql_sessions, (user_id,))

        if not sessions:
            return {
                'has_data': False,
                'total_interviews': 0,
                'average_score': 0.0,
                'technical_avg': 0.0,
                'hr_avg': 0.0,
                'timeline_labels': [],
                'timeline_scores': [],
                'category_labels': ["Technical", "HR"],
                'category_scores': [0, 0],
                'strong_topics': [],
                'weak_topics': [],
                'sessions_history': [],
                'ai_recommendations': "You have not completed any mock interviews yet. Take your first AI Mock Interview to receive tailored performance insights, radar charts, and personalized study paths!"
            }

        # Calculate metrics from completed sessions
        session_ids = [s['id'] for s in sessions]
        total_interviews = len(sessions)
        valid_scores = [float(s['overall_score']) for s in sessions if s['overall_score'] is not None]
        avg_score = round(sum(valid_scores) / len(valid_scores), 1) if valid_scores else 0.0

        # Timeline data (chronological)
        timeline_labels = [f"#{i+1} - {s['company_name'][:10]} ({s['created_at'][:10] if s.get('created_at') else ''})" for i, s in enumerate(sessions)]
        timeline_scores = [float(s['overall_score'] or 0) for s in sessions]

        # Fetch all questions for completed sessions
        placeholders = ','.join(['%s'] * len(session_ids))
        sql_questions = f"""
        SELECT q.*, s.company_name, s.job_role, s.interview_category as session_category
        FROM mock_interview_questions q
        JOIN mock_interview_sessions s ON q.session_id = s.id
        WHERE q.session_id IN ({placeholders}) AND q.overall_question_score IS NOT NULL
        """
        questions = query_all(sql_questions, tuple(session_ids))

        # Technical vs HR split
        tech_scores = [float(q['overall_question_score']) for q in questions if q.get('question_category') == 'Technical']
        hr_scores = [float(q['overall_question_score']) for q in questions if q.get('question_category') == 'HR']

        tech_avg = round(sum(tech_scores) / len(tech_scores), 1) if tech_scores else round(avg_score, 1)
        hr_avg = round(sum(hr_scores) / len(hr_scores), 1) if hr_scores else round(avg_score, 1)

        # Topic aggregation: identify strong and weak areas from feedback and rubric scores
        high_scoring = [q for q in questions if float(q['overall_question_score'] or 0) >= 80.0]
        low_scoring = [q for q in questions if float(q['overall_question_score'] or 0) < 70.0]

        strong_topics = []
        for q in high_scoring[:5]:
            # Extract concise topic hint
            q_hint = q['question'][:45] + ("..." if len(q['question']) > 45 else "")
            strong_topics.append({
                'topic': q_hint,
                'score': float(q['overall_question_score']),
                'feedback': q['strengths'] or 'Clear and well-structured answer.'
            })

        weak_topics = []
        for q in low_scoring[:5]:
            q_hint = q['question'][:45] + ("..." if len(q['question']) > 45 else "")
            weak_topics.append({
                'topic': q_hint,
                'score': float(q['overall_question_score']),
                'feedback': q['weaknesses'] or 'Needs deeper explanation of edge cases or trade-offs.'
            })

        # Generate personalized AI recommendations if enough data
        ai_recommendation = PerformanceAnalysisService._generate_ai_recommendations(
            sessions, questions, avg_score, tech_avg, hr_avg, user_id
        )

        return {
            'has_data': True,
            'total_interviews': total_interviews,
            'average_score': avg_score,
            'technical_avg': tech_avg,
            'hr_avg': hr_avg,
            'timeline_labels': timeline_labels,
            'timeline_scores': timeline_scores,
            'category_labels': ["Technical Rounds", "HR & Behavioral"],
            'category_scores': [tech_avg, hr_avg],
            'strong_topics': strong_topics,
            'weak_topics': weak_topics,
            'sessions_history': list(reversed(sessions)),
            'ai_recommendations': ai_recommendation
        }

    @staticmethod
    def _generate_ai_recommendations(sessions: List[Dict], questions: List[Dict],
                                     avg_score: float, tech_avg: float, hr_avg: float,
                                     user_id: int) -> str:
        provider = AIFactory.get_provider()
        
        sample_questions = [
            f"- Q: {q['question'][:80]} | Score: {q.get('overall_question_score')}% | Weakness: {q.get('weaknesses', '')[:100]}"
            for q in questions[:6]
        ]
        q_summary = "\n".join(sample_questions)

        prompt = f"""
Act as an elite technical career mentor. Provide personalized performance analysis recommendations based on the candidate's actual mock interview trajectory:
- Total Completed Mock Interviews: {len(sessions)}
- Average Overall Score: {avg_score}%
- Technical Average: {tech_avg}%
- HR/Behavioral Average: {hr_avg}%

Recent Question Samples and Evaluations:
{q_summary}

Provide a concise, encouraging 3-paragraph diagnostic:
1. Analysis of overall trajectory and current readiness level.
2. High-priority technical focus areas and recurring mistakes identified in answers.
3. Concrete weekly study plan to raise performance in upcoming company interviews.
"""
        res = provider.generate_text(prompt=prompt, temperature=0.6, max_tokens=600)
        
        AIDaO.log_ai_usage(
            user_id=user_id,
            feature_name="performance_recommendations",
            provider=res.get('provider', 'unknown'),
            model_name=res.get('model', 'unknown'),
            status=res.get('status', 'error'),
            prompt_tokens=res.get('prompt_tokens', 0),
            completion_tokens=res.get('completion_tokens', 0),
            token_usage=res.get('total_tokens', 0),
            estimated_cost=AIFactory.calculate_cost(
                res.get('provider', ''), res.get('model', ''),
                res.get('prompt_tokens', 0), res.get('completion_tokens', 0)
            ),
            error_message=res.get('error')
        )

        if res['status'] == 'success' and res['content']:
            return res['content'].strip()

        # Fallback diagnostic
        return f"""
Based on your {len(sessions)} completed mock interview session(s), you have established an overall performance average of {avg_score}%. Your technical round average stands at {tech_avg}%, while your behavioral/HR evaluations average {hr_avg}%.

To optimize your interview readiness:
1. Continue practicing system design and algorithm questions to improve your technical score benchmark.
2. Structure all behavioral answers with the STAR format (Situation, Task, Action, Result) to maximize clarity scores.
3. Focus on explaining edge-case handling and asymptotic complexities before writing solution code.
"""
