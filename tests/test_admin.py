import pytest
from dao.user_dao import UserDAO
from dao.company_dao import CompanyDAO
from dao.ai_dao import AIDaO

def test_admin_login_success(client, admin_account):
    res = client.post('/admin/login', data={
        'username': admin_account.username,
        'password': 'AdminPass123!'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Admin Control Dashboard" in res.data or b"Control Dashboard" in res.data

def test_admin_login_failure(client, admin_account):
    res = client.post('/admin/login', data={
        'username': admin_account.username,
        'password': 'WrongPassword123!'
    }, follow_redirects=True)
    assert b"Invalid administrator credentials" in res.data

def test_admin_route_protection_unauthorized(client):
    res = client.get('/admin/dashboard')
    assert res.status_code == 302
    assert '/admin/login' in res.location

def test_admin_dashboard_metrics(admin_client):
    res = admin_client.get('/admin/dashboard')
    assert res.status_code == 200
    assert b"System Control Dashboard" in res.data

def test_admin_toggle_user_status(admin_client):
    # Create target test user
    uid = UserDAO.create_user("Status User", "statususer@portal.com", "hash123", "student")
    user = UserDAO.get_by_id(uid)
    assert user.is_active is True

    # Toggle to deactivated
    res = admin_client.post('/admin/users', data={
        'action': 'toggle_status',
        'user_id': uid
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"User account deactivated" in res.data

    user = UserDAO.get_by_id(uid)
    assert user.is_active is False

    # Toggle back to active
    admin_client.post('/admin/users', data={
        'action': 'toggle_status',
        'user_id': uid
    }, follow_redirects=True)
    user = UserDAO.get_by_id(uid)
    assert user.is_active is True

def test_admin_company_crud(admin_client):
    # Create company
    res = admin_client.post('/admin/companies', data={
        'action': 'create',
        'company_name': 'Spotify Tech',
        'description': 'Audio streaming platform',
        'website': 'https://careers.spotify.com'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Spotify Tech" in res.data

    comp = CompanyDAO.get_by_name('Spotify Tech')
    assert comp is not None

    # Update company
    admin_client.post('/admin/companies', data={
        'action': 'update',
        'company_id': comp.id,
        'company_name': 'Spotify Technology SA',
        'description': 'Updated music streaming description',
        'website': 'https://spotify.com/jobs'
    }, follow_redirects=True)

    updated_comp = CompanyDAO.get_by_id(comp.id)
    assert updated_comp.company_name == 'Spotify Technology SA'

    # Delete company
    admin_client.post('/admin/companies', data={
        'action': 'delete',
        'company_id': comp.id
    }, follow_redirects=True)

    assert CompanyDAO.get_by_id(comp.id) is None

def test_admin_ai_usage_page(admin_client):
    res = admin_client.get('/admin/ai-usage')
    assert res.status_code == 200
    assert b"AI Usage" in res.data
