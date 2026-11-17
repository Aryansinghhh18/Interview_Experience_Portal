from werkzeug.security import generate_password_hash, check_password_hash

class User:
    def __init__(self, id=None, name=None, email=None, password_hash=None, role='student', is_active=True, created_at=None, updated_at=None):
        self.id = id
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.is_active = bool(is_active)
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def hash_password(password: str) -> str:
        return generate_password_hash(password, method='scrypt')

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def is_admin(self) -> bool:
        return self.role == 'admin'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': str(self.created_at) if self.created_at else None,
            'updated_at': str(self.updated_at) if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data):
        if not data:
            return None
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            email=data.get('email'),
            password_hash=data.get('password_hash'),
            role=data.get('role', 'student'),
            is_active=data.get('is_active', True),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )


class Admin:
    def __init__(self, id=None, username=None, email=None, password_hash=None, is_active=True, created_at=None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.is_active = bool(is_active)
        self.created_at = created_at

    @staticmethod
    def hash_password(password: str) -> str:
        return generate_password_hash(password, method='scrypt')

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'created_at': str(self.created_at) if self.created_at else None,
        }

    @classmethod
    def from_dict(cls, data):
        if not data:
            return None
        return cls(
            id=data.get('id'),
            username=data.get('username'),
            email=data.get('email'),
            password_hash=data.get('password_hash'),
            is_active=data.get('is_active', True),
            created_at=data.get('created_at')
        )
