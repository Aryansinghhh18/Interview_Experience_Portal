import pytest
from dao.company_dao import CompanyDAO
from dao.experience_dao import ExperienceDAO

def test_add_experience_pending_approval(auth_client, user_account):
    res = auth_client.post('/experiences/add', data={
        'company_name': 'Netflix',
        'job_role': 'Streaming Backend Engineer',
        'interview_date': '2026-04-10',
        'interview_type': 'Online',
        'difficulty': 'Hard',
        'experience_level': 'Mid Level',
        'interview_rounds': 4,
        'technical_questions': '1. Design distributed video transcoding queue with Kafka.\n2. In-memory caching with Redis.',
        'hr_questions': 'Why Netflix culture memo?',
        'overall_experience': 'Intense architectural deep dives with senior staff engineers. Very positive atmosphere.',
        'preparation_tips': 'Study system design, distributed consensus, and microservices.',
        'result': 'Selected'
    }, follow_redirects=True)

    assert res.status_code == 200
    assert b"submitted for administrator review" in res.data

    # Verify status is pending in DB
    my_exps = ExperienceDAO.get_user_experiences(user_account.id)
    netflix_exp = [e for e in my_exps if e.company_name == 'Netflix'][0]
    assert netflix_exp.approval_status == 'pending'

    # Verify pending experience is NOT visible in public approved exploration
    public_res = auth_client.get('/experiences?company=Netflix')
    assert b"Streaming Backend Engineer" not in public_res.data

def test_admin_approve_experience(admin_client, user_account):
    # Find pending Netflix experience
    my_exps = ExperienceDAO.get_user_experiences(user_account.id)
    netflix_exp = [e for e in my_exps if e.company_name == 'Netflix'][0]

    # Approve as admin
    res = admin_client.post('/admin/experiences', data={
        'action': 'approve',
        'experience_id': netflix_exp.id
    }, follow_redirects=True)

    assert res.status_code == 200
    assert b"Experience approved successfully" in res.data

    # Verify now visible in public exploration
    public_res = admin_client.get('/experiences?company=Netflix')
    assert b"Streaming Backend Engineer" in public_res.data

def test_experience_filtering(client):
    # Filter by Hard difficulty
    res = client.get('/experiences?difficulty=Hard')
    assert res.status_code == 200
    assert b"Hard" in res.data

def test_experience_editing_resets_pending(auth_client, user_account):
    my_exps = ExperienceDAO.get_user_experiences(user_account.id)
    netflix_exp = [e for e in my_exps if e.company_name == 'Netflix'][0]

    # Edit experience
    res = auth_client.post(f'/experiences/{netflix_exp.id}/edit', data={
        'company_name': 'Netflix',
        'job_role': 'Lead Distributed Systems Engineer',
        'interview_date': '2026-04-10',
        'interview_type': 'Online',
        'difficulty': 'Hard',
        'experience_level': 'Senior',
        'interview_rounds': 5,
        'technical_questions': 'Updated technical questions on distributed consensus Raft.',
        'hr_questions': 'Cultural fit questions.',
        'overall_experience': 'Updated experience text with more comprehensive details about the process.',
        'preparation_tips': 'Read Designing Data-Intensive Applications.',
        'result': 'Selected'
    }, follow_redirects=True)

    assert res.status_code == 200
    assert b"awaiting administrator re-approval" in res.data

    updated_exp = ExperienceDAO.get_by_id(netflix_exp.id)
    assert updated_exp.job_role == 'Lead Distributed Systems Engineer'
    assert updated_exp.approval_status == 'pending'

def test_experience_deletion(auth_client, user_account):
    my_exps = ExperienceDAO.get_user_experiences(user_account.id)
    netflix_exp = [e for e in my_exps if e.company_name == 'Netflix'][0]

    res = auth_client.post(f'/experiences/{netflix_exp.id}/delete', follow_redirects=True)
    assert res.status_code == 200
    assert b"deleted successfully" in res.data

    assert ExperienceDAO.get_by_id(netflix_exp.id) is None
