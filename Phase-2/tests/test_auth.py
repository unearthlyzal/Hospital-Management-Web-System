import json
import pytest
from models import User
from werkzeug.security import generate_password_hash

def test_login_success(client, session):
    # Create test user
    hashed_password = generate_password_hash('TestPass123!')
    user = User(
        id='TEST001',
        username='testuser',
        password=hashed_password,
        email='test@example.com',
        role='Patient',
        is_active=True
    )
    session.add(user)
    session.commit()

    # Test login
    response = client.post('/api/login', json={
        'username': 'testuser',
        'password': 'TestPass123!'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'token' in data
    assert data['user_id'] == 'TEST001'
    assert data['role'] == 'Patient'

def test_login_invalid_credentials(client):
    response = client.post('/api/login', json={
        'username': 'nonexistent',
        'password': 'wrong'
    })
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data['message'] == 'Invalid username or password'

def test_protected_route_without_token(client):
    response = client.get('/api/users/profile')
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data['message'] == 'Missing token'

def test_protected_route_with_invalid_token(client):
    headers = {'Authorization': 'Bearer invalid-token'}
    response = client.get('/api/users/profile', headers=headers)
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data['message'] == 'Invalid or expired token'

def test_role_based_access(client, session):
    # Create test user with Patient role
    hashed_password = generate_password_hash('TestPass123!')
    user = User(
        id='TEST002',
        username='testpatient',
        password=hashed_password,
        email='patient@example.com',
        role='Patient',
        is_active=True
    )
    session.add(user)
    session.commit()

    # Login to get token
    response = client.post('/api/login', json={
        'username': 'testpatient',
        'password': 'TestPass123!'
    })
    token = json.loads(response.data)['token']
    headers = {'Authorization': f'Bearer {token}'}

    # Try to access admin-only endpoint
    response = client.get('/api/admin/users', headers=headers)
    assert response.status_code == 403
    data = json.loads(response.data)
    assert data['message'] == 'Insufficient permissions' 