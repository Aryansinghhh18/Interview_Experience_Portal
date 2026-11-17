import pytest
from models.user import User
from dao.user_dao import UserDAO

def test_password_hashing():
    raw_pw = "SuperSecurePassword123!"
    hash_pw = User.hash_password(raw_pw)
    assert hash_pw != raw_pw
    user = User(password_hash=hash_pw)
    assert user.check_password(raw_pw) is True
    assert user.check_password("WrongPassword") is False

def test_registration_success(client):
    res = client.post('/register', data={
        'name': 'Alice Candidate',
        'email': 'alice@example.com',
        'password': 'SecurePass123!',
        'confirm_password': 'SecurePass123!',
        'role': 'student'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Registration successful" in res.data
    
    user = UserDAO.get_by_email('alice@example.com')
    assert user is not None
    assert user.name == 'Alice Candidate'

def test_duplicate_registration_prevention(client):
    res = client.post('/register', data={
        'name': 'Duplicate User',
        'email': 'alice@example.com',
        'password': 'SecurePass123!',
        'confirm_password': 'SecurePass123!',
        'role': 'student'
    }, follow_redirects=True)
    assert b"already exists" in res.data

def test_registration_mismatched_password(client):
    res = client.post('/register', data={
        'name': 'Mismatch User',
        'email': 'mismatch@example.com',
        'password': 'Password1!',
        'confirm_password': 'Password2!',
        'role': 'student'
    }, follow_redirects=True)
    assert b"do not match" in res.data

def test_user_login_success(client, user_account):
    res = client.post('/login', data={
        'email': user_account.email,
        'password': 'Password123!'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Welcome back" in res.data

def test_user_login_invalid_password(client, user_account):
    res = client.post('/login', data={
        'email': user_account.email,
        'password': 'IncorrectPassword!'
    }, follow_redirects=True)
    assert b"Invalid email or password" in res.data

def test_unauthorized_dashboard_access_redirect(client):
    res = client.get('/dashboard')
    assert res.status_code == 302
    assert '/login' in res.location

def test_logout(auth_client):
    res = auth_client.get('/logout', follow_redirects=True)
    assert res.status_code == 200
    assert b"signed out successfully" in res.data
