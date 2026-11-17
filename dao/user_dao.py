from database import query_one, query_all, execute_insert, execute
from models.user import User, Admin

class UserDAO:
    @staticmethod
    def create_user(name, email, password_hash, role='student'):
        sql = """
        INSERT INTO users (name, email, password_hash, role, is_active)
        VALUES (%s, %s, %s, %s, %s)
        """
        user_id = execute_insert(sql, (name, email.lower().strip(), password_hash, role, 1))
        return user_id

    @staticmethod
    def get_by_id(user_id):
        sql = "SELECT * FROM users WHERE id = %s"
        row = query_one(sql, (user_id,))
        return User.from_dict(row) if row else None

    @staticmethod
    def get_by_email(email):
        sql = "SELECT * FROM users WHERE LOWER(email) = %s"
        row = query_one(sql, (email.lower().strip(),))
        return User.from_dict(row) if row else None

    @staticmethod
    def update_user(user_id, name=None, email=None, password_hash=None, is_active=None):
        updates = []
        params = []
        if name is not None:
            updates.append("name = %s")
            params.append(name)
        if email is not None:
            updates.append("email = %s")
            params.append(email.lower().strip())
        if password_hash is not None:
            updates.append("password_hash = %s")
            params.append(password_hash)
        if is_active is not None:
            updates.append("is_active = %s")
            params.append(1 if is_active else 0)
            
        if not updates:
            return False
            
        params.append(user_id)
        sql = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
        return execute(sql, tuple(params)) > 0

    @staticmethod
    def delete_user(user_id):
        sql = "DELETE FROM users WHERE id = %s"
        return execute(sql, (user_id,)) > 0

    @staticmethod
    def get_all(search=None, limit=50, offset=0):
        if search:
            search_param = f"%{search.strip()}%"
            sql = """
            SELECT * FROM users 
            WHERE name LIKE %s OR email LIKE %s 
            ORDER BY created_at DESC LIMIT %s OFFSET %s
            """
            rows = query_all(sql, (search_param, search_param, limit, offset))
        else:
            sql = "SELECT * FROM users ORDER BY created_at DESC LIMIT %s OFFSET %s"
            rows = query_all(sql, (limit, offset))
        return [User.from_dict(r) for r in rows]

    @staticmethod
    def count_users(search=None):
        if search:
            search_param = f"%{search.strip()}%"
            sql = "SELECT COUNT(*) as c FROM users WHERE name LIKE %s OR email LIKE %s"
            row = query_one(sql, (search_param, search_param))
        else:
            sql = "SELECT COUNT(*) as c FROM users"
            row = query_one(sql)
        return row['c'] if row else 0


class AdminDAO:
    @staticmethod
    def create_admin(username, email, password_hash):
        sql = """
        INSERT INTO admins (username, email, password_hash, is_active)
        VALUES (%s, %s, %s, %s)
        """
        return execute_insert(sql, (username.strip(), email.lower().strip(), password_hash, 1))

    @staticmethod
    def get_by_id(admin_id):
        sql = "SELECT * FROM admins WHERE id = %s"
        row = query_one(sql, (admin_id,))
        return Admin.from_dict(row) if row else None

    @staticmethod
    def get_by_username(username):
        sql = "SELECT * FROM admins WHERE LOWER(username) = %s"
        row = query_one(sql, (username.lower().strip(),))
        return Admin.from_dict(row) if row else None

    @staticmethod
    def get_by_email(email):
        sql = "SELECT * FROM admins WHERE LOWER(email) = %s"
        row = query_one(sql, (email.lower().strip(),))
        return Admin.from_dict(row) if row else None
