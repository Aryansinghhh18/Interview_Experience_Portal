import os
import sys
import tempfile
import pytest
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from config import Config
from database import init_db
from app import create_app
from services.ai.ai_factory import AIFactory
from models.user import User, Admin
from dao.user_dao import UserDAO, AdminDAO
from dao.company_dao import CompanyDAO
from dao.experience_dao import ExperienceDAO

class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "test-secret-key"
    USE_SQLITE_FALLBACK = True
    SQLITE_DB_PATH = Path(tempfile.gettempdir()) / "test_interview_portal.db"
    AI_PROVIDER = "mock"

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    # Force mock AI provider for all automated tests
    AIFactory.set_force_mock(True)
    
    # Clean previous test database
    if TestConfig.SQLITE_DB_PATH.exists():
        try:
            os.remove(TestConfig.SQLITE_DB_PATH)
        except Exception:
            pass

    # Initialize tables
    Config.USE_SQLITE_FALLBACK = True
    Config.SQLITE_DB_PATH = TestConfig.SQLITE_DB_PATH
    init_db()

@pytest.fixture
def app():
    app = create_app(TestConfig)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def user_account():
    email = "teststudent@portal.com"
    user = UserDAO.get_by_email(email)
    if not user:
        uid = UserDAO.create_user("Test Student", email, User.hash_password("Password123!"), role='student')
        user = UserDAO.get_by_id(uid)
    return user

@pytest.fixture
def auth_client(client, user_account):
    client.post('/login', data={
        'email': user_account.email,
        'password': 'Password123!'
    }, follow_redirects=True)
    return client

@pytest.fixture
def admin_account():
    username = "testadmin"
    email = "admin@portaltest.com"
    admin = AdminDAO.get_by_username(username)
    if not admin:
        aid = AdminDAO.create_admin(username, email, Admin.hash_password("AdminPass123!"))
        admin = AdminDAO.get_by_id(aid)
    return admin

@pytest.fixture
def admin_client(client, admin_account):
    client.post('/admin/login', data={
        'username': admin_account.username,
        'password': 'AdminPass123!'
    }, follow_redirects=True)
    return client
