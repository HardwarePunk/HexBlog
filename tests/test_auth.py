"""Authentication tests"""
import pytest
from flask import session
from app.models.user import User
from app import db

def test_login(client, auth):
    """Test login functionality."""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Login' in response.data

    # Test invalid credentials
    response = auth.login('wrong@test.com', 'wrong')
    assert b'Invalid email or password' in response.data

    # Test valid credentials
    response = auth.login()
    assert response.headers['Location'] == '/'

def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post('/auth/login', data={
        'email': 'wrong@test.com',
        'password': 'wrong'
    })
    assert b'Invalid email or password' in response.data

def test_logout(client, auth):
    """Test logout functionality."""
    auth.login()
    with client:
        auth.logout()
        assert '_user_id' not in session

def test_register(client, auth, app):
    """Test user registration."""
    # Login as admin and enable registration
    auth.login()
    with app.app_context():
        current_user = User.query.filter_by(email='admin@test.com').first()
        current_user.registration_enabled = True
        db.session.commit()
    
    auth.logout()
    
    # Test registration page loads
    response = client.get('/auth/register')
    assert response.status_code == 200
    assert b'Register' in response.data
    
    # Test successful registration
    response = client.post(
        '/auth/register',
        data={
            'email': 'newuser@test.com',
            'username': 'newuser',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }
    )
    assert response.headers['Location'] == '/auth/login'

def test_register_validation(client, auth, app):
    """Test registration validation."""
    # Login as admin and enable registration
    auth.login()
    with app.app_context():
        current_user = User.query.filter_by(email='admin@test.com').first()
        current_user.registration_enabled = True
        db.session.commit()
    
    auth.logout()
    
    # Test password mismatch
    response = client.post(
        '/auth/register',
        data={
            'email': 'test@test.com',
            'username': 'test',
            'password': 'testpass123',
            'password_confirm': 'wrongpass'
        }
    )
    assert b'Passwords must match' in response.data
    
    # Test invalid email
    response = client.post(
        '/auth/register',
        data={
            'email': 'invalid-email',
            'username': 'test',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
    )
    assert b'Invalid email address' in response.data

def test_registration_disabled(client, auth, app):
    """Test registration when disabled."""
    # Login as admin and disable registration
    auth.login()
    with app.app_context():
        current_user = User.query.filter_by(email='admin@test.com').first()
        current_user.registration_enabled = False
        db.session.commit()
    
    auth.logout()
    
    # Try to access registration page
    response = client.get('/auth/register')
    assert response.headers['Location'] == '/auth/login'
    assert b'Registration is currently disabled' in client.get('/auth/login').data

def test_toggle_registration(client, auth, app):
    """Test toggling registration."""
    auth.login()
    
    # Test enabling registration
    response = client.post('/admin/users/toggle-registration', data={
        'registration_enabled': 'on'
    })
    assert response.headers['Location'] == '/admin/users'
    
    with app.app_context():
        admin = User.query.filter_by(email='admin@test.com').first()
        assert admin.registration_enabled is True
    
    # Test disabling registration
    response = client.post('/admin/users/toggle-registration', data={})
    assert response.headers['Location'] == '/admin/users'
    
    with app.app_context():
        admin = User.query.filter_by(email='admin@test.com').first()
        assert admin.registration_enabled is False

def test_admin_user_list(client, auth, app):
    """Test that admin users are filtered out of user list."""
    auth.login()
    
    # Create a regular user
    with app.app_context():
        regular_user = User(
            email='regular@test.com',
            username='regular',
            display_name='Regular User',
            active=True,
            is_approved=True
        )
        regular_user.set_password('password123')
        db.session.add(regular_user)
        db.session.commit()
    
    # Check user list
    response = client.get('/admin/users')
    assert response.status_code == 200
    assert b'regular@test.com' in response.data
    assert b'admin@test.com' not in response.data  # Admin should not be in list
