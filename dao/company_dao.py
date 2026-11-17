from database import query_one, query_all, execute_insert, execute
from models.company import Company

class CompanyDAO:
    @staticmethod
    def get_or_create(company_name, description=None, website=None):
        cleaned_name = company_name.strip()
        existing = CompanyDAO.get_by_name(cleaned_name)
        if existing:
            return existing.id
        
        sql = """
        INSERT INTO companies (company_name, description, website)
        VALUES (%s, %s, %s)
        """
        return execute_insert(sql, (cleaned_name, description, website))

    @staticmethod
    def create(company_name, description=None, website=None):
        sql = """
        INSERT INTO companies (company_name, description, website)
        VALUES (%s, %s, %s)
        """
        return execute_insert(sql, (company_name.strip(), description, website))

    @staticmethod
    def get_by_id(company_id):
        sql = "SELECT * FROM companies WHERE id = %s"
        row = query_one(sql, (company_id,))
        return Company.from_dict(row) if row else None

    @staticmethod
    def get_by_name(company_name):
        sql = "SELECT * FROM companies WHERE LOWER(company_name) = %s"
        row = query_one(sql, (company_name.strip().lower(),))
        return Company.from_dict(row) if row else None

    @staticmethod
    def get_all(search=None, limit=100, offset=0):
        if search:
            param = f"%{search.strip()}%"
            sql = """
            SELECT c.*, COUNT(e.id) as experience_count 
            FROM companies c
            LEFT JOIN interview_experiences e ON c.id = e.company_id AND e.approval_status = 'approved'
            WHERE c.company_name LIKE %s
            GROUP BY c.id
            ORDER BY c.company_name ASC
            LIMIT %s OFFSET %s
            """
            rows = query_all(sql, (param, limit, offset))
        else:
            sql = """
            SELECT c.*, COUNT(e.id) as experience_count 
            FROM companies c
            LEFT JOIN interview_experiences e ON c.id = e.company_id AND e.approval_status = 'approved'
            GROUP BY c.id
            ORDER BY c.company_name ASC
            LIMIT %s OFFSET %s
            """
            rows = query_all(sql, (limit, offset))
        return rows

    @staticmethod
    def update(company_id, company_name, description=None, website=None):
        sql = """
        UPDATE companies 
        SET company_name = %s, description = %s, website = %s
        WHERE id = %s
        """
        return execute(sql, (company_name.strip(), description, website, company_id)) > 0

    @staticmethod
    def delete(company_id):
        sql = "DELETE FROM companies WHERE id = %s"
        return execute(sql, (company_id,)) > 0

    @staticmethod
    def count(search=None):
        if search:
            param = f"%{search.strip()}%"
            sql = "SELECT COUNT(*) as c FROM companies WHERE company_name LIKE %s"
            row = query_one(sql, (param,))
        else:
            sql = "SELECT COUNT(*) as c FROM companies"
            row = query_one(sql)
        return row['c'] if row else 0

    @staticmethod
    def get_popular(limit=10):
        sql = """
        SELECT c.id, c.company_name, COUNT(e.id) as experience_count
        FROM companies c
        JOIN interview_experiences e ON c.id = e.company_id
        WHERE e.approval_status = 'approved'
        GROUP BY c.id, c.company_name
        ORDER BY experience_count DESC
        LIMIT %s
        """
        return query_all(sql, (limit,))
