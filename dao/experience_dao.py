from database import query_one, query_all, execute_insert, execute
from models.experience import InterviewExperience

class ExperienceDAO:
    @staticmethod
    def create(user_id, company_id, job_role, interview_date, interview_type,
               difficulty, experience_level, interview_rounds, technical_questions,
               hr_questions, overall_experience, preparation_tips, result, approval_status='pending'):
        sql = """
        INSERT INTO interview_experiences (
            user_id, company_id, job_role, interview_date, interview_type,
            difficulty, experience_level, interview_rounds, technical_questions,
            hr_questions, overall_experience, preparation_tips, result, approval_status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        return execute_insert(sql, (
            user_id, company_id, job_role.strip(), interview_date, interview_type,
            difficulty, experience_level, interview_rounds, technical_questions,
            hr_questions, overall_experience, preparation_tips, result, approval_status
        ))

    @staticmethod
    def get_by_id(exp_id):
        sql = """
        SELECT e.*, c.company_name, u.name as user_name
        FROM interview_experiences e
        JOIN companies c ON e.company_id = c.id
        JOIN users u ON e.user_id = u.id
        WHERE e.id = %s
        """
        row = query_one(sql, (exp_id,))
        return InterviewExperience.from_dict(row) if row else None

    @staticmethod
    def get_user_experiences(user_id):
        sql = """
        SELECT e.*, c.company_name, u.name as user_name
        FROM interview_experiences e
        JOIN companies c ON e.company_id = c.id
        JOIN users u ON e.user_id = u.id
        WHERE e.user_id = %s
        ORDER BY e.created_at DESC
        """
        rows = query_all(sql, (user_id,))
        return [InterviewExperience.from_dict(r) for r in rows]

    @staticmethod
    def get_approved(company=None, role=None, difficulty=None, experience_level=None, search=None, limit=20, offset=0):
        where_clauses = ["e.approval_status = 'approved'"]
        params = []

        if company:
            where_clauses.append("LOWER(c.company_name) LIKE %s")
            params.append(f"%{company.lower().strip()}%")
        if role:
            where_clauses.append("LOWER(e.job_role) LIKE %s")
            params.append(f"%{role.lower().strip()}%")
        if difficulty:
            where_clauses.append("e.difficulty = %s")
            params.append(difficulty)
        if experience_level:
            where_clauses.append("e.experience_level = %s")
            params.append(experience_level)
        if search:
            where_clauses.append("""
            (c.company_name LIKE %s OR e.job_role LIKE %s OR e.technical_questions LIKE %s OR e.overall_experience LIKE %s)
            """)
            param = f"%{search.strip()}%"
            params.extend([param, param, param, param])

        where_sql = " AND ".join(where_clauses)
        params.extend([limit, offset])

        sql = f"""
        SELECT e.*, c.company_name, u.name as user_name
        FROM interview_experiences e
        JOIN companies c ON e.company_id = c.id
        JOIN users u ON e.user_id = u.id
        WHERE {where_sql}
        ORDER BY e.created_at DESC
        LIMIT %s OFFSET %s
        """
        rows = query_all(sql, tuple(params))
        return [InterviewExperience.from_dict(r) for r in rows]

    @staticmethod
    def count_approved(company=None, role=None, difficulty=None, experience_level=None, search=None):
        where_clauses = ["e.approval_status = 'approved'"]
        params = []

        if company:
            where_clauses.append("LOWER(c.company_name) LIKE %s")
            params.append(f"%{company.lower().strip()}%")
        if role:
            where_clauses.append("LOWER(e.job_role) LIKE %s")
            params.append(f"%{role.lower().strip()}%")
        if difficulty:
            where_clauses.append("e.difficulty = %s")
            params.append(difficulty)
        if experience_level:
            where_clauses.append("e.experience_level = %s")
            params.append(experience_level)
        if search:
            where_clauses.append("""
            (c.company_name LIKE %s OR e.job_role LIKE %s OR e.technical_questions LIKE %s OR e.overall_experience LIKE %s)
            """)
            param = f"%{search.strip()}%"
            params.extend([param, param, param, param])

        where_sql = " AND ".join(where_clauses)
        sql = f"""
        SELECT COUNT(*) as c
        FROM interview_experiences e
        JOIN companies c ON e.company_id = c.id
        WHERE {where_sql}
        """
        row = query_one(sql, tuple(params))
        return row['c'] if row else 0

    @staticmethod
    def get_recent_approved(limit=6):
        sql = """
        SELECT e.*, c.company_name, u.name as user_name
        FROM interview_experiences e
        JOIN companies c ON e.company_id = c.id
        JOIN users u ON e.user_id = u.id
        WHERE e.approval_status = 'approved'
        ORDER BY e.created_at DESC
        LIMIT %s
        """
        rows = query_all(sql, (limit,))
        return [InterviewExperience.from_dict(r) for r in rows]

    @staticmethod
    def get_all_admin(status=None, search=None, limit=50, offset=0):
        where = []
        params = []
        if status:
            where.append("e.approval_status = %s")
            params.append(status)
        if search:
            where.append("(c.company_name LIKE %s OR e.job_role LIKE %s OR u.name LIKE %s)")
            p = f"%{search.strip()}%"
            params.extend([p, p, p])
            
        where_sql = f"WHERE {' AND '.join(where)}" if where else ""
        params.extend([limit, offset])

        sql = f"""
        SELECT e.*, c.company_name, u.name as user_name, u.email as user_email
        FROM interview_experiences e
        JOIN companies c ON e.company_id = c.id
        JOIN users u ON e.user_id = u.id
        {where_sql}
        ORDER BY e.created_at DESC
        LIMIT %s OFFSET %s
        """
        return query_all(sql, tuple(params))

    @staticmethod
    def count_all_admin(status=None, search=None):
        where = []
        params = []
        if status:
            where.append("e.approval_status = %s")
            params.append(status)
        if search:
            where.append("(c.company_name LIKE %s OR e.job_role LIKE %s OR u.name LIKE %s)")
            p = f"%{search.strip()}%"
            params.extend([p, p, p])
            
        where_sql = f"WHERE {' AND '.join(where)}" if where else ""
        sql = f"""
        SELECT COUNT(*) as c
        FROM interview_experiences e
        JOIN companies c ON e.company_id = c.id
        JOIN users u ON e.user_id = u.id
        {where_sql}
        """
        row = query_one(sql, tuple(params))
        return row['c'] if row else 0

    @staticmethod
    def update_approval(exp_id, status, rejection_reason=None):
        sql = """
        UPDATE interview_experiences 
        SET approval_status = %s, rejection_reason = %s
        WHERE id = %s
        """
        return execute(sql, (status, rejection_reason, exp_id)) > 0

    @staticmethod
    def update(exp_id, user_id, company_id, job_role, interview_date,
               interview_type, difficulty, experience_level, interview_rounds,
               technical_questions, hr_questions, overall_experience,
               preparation_tips, result, reset_approval=True):
        status_part = ", approval_status = 'pending'" if reset_approval else ""
        sql = f"""
        UPDATE interview_experiences 
        SET company_id = %s, job_role = %s, interview_date = %s, interview_type = %s,
            difficulty = %s, experience_level = %s, interview_rounds = %s,
            technical_questions = %s, hr_questions = %s, overall_experience = %s,
            preparation_tips = %s, result = %s {status_part}
        WHERE id = %s AND user_id = %s
        """
        return execute(sql, (
            company_id, job_role.strip(), interview_date, interview_type,
            difficulty, experience_level, interview_rounds,
            technical_questions, hr_questions, overall_experience,
            preparation_tips, result, exp_id, user_id
        )) > 0

    @staticmethod
    def delete(exp_id, user_id=None):
        if user_id:
            sql = "DELETE FROM interview_experiences WHERE id = %s AND user_id = %s"
            return execute(sql, (exp_id, user_id)) > 0
        else:
            sql = "DELETE FROM interview_experiences WHERE id = %s"
            return execute(sql, (exp_id,)) > 0

    @staticmethod
    def get_stats():
        sql = """
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN approval_status = 'approved' THEN 1 ELSE 0 END) as approved,
            SUM(CASE WHEN approval_status = 'pending' THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN approval_status = 'rejected' THEN 1 ELSE 0 END) as rejected,
            SUM(CASE WHEN result = 'Selected' AND approval_status = 'approved' THEN 1 ELSE 0 END) as selected
        FROM interview_experiences
        """
        row = query_one(sql)
        return {
            'total': row['total'] if row and row['total'] else 0,
            'approved': row['approved'] if row and row['approved'] else 0,
            'pending': row['pending'] if row and row['pending'] else 0,
            'rejected': row['rejected'] if row and row['rejected'] else 0,
            'selected': row['selected'] if row and row['selected'] else 0,
        }
