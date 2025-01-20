"""Authentication tests"""
import pytest
from flask import session

def test_login(client, auth):
    """Test login functionality."""
    # Test login page loads
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Login' in response.data
    
    # Test successful login
    response = auth.login()
    assert response.headers['Location'] == '/'
    
    # Test logged in user can access protected pages
    with client:
        client.get('/')
        assert session['_user_id'] is not None

def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post(
        '/auth/login',
        data={'email': 'wrong@test.com', 'password': 'wrongpass'}
    )
    assert b'Invalid email or password' in response.data

def test_logout(client, auth):
    """Test logout functionality."""
    auth.login()
    
    with client:
        auth.logout()
        assert '_user_id' not in session

def test_register(client):
    """Test user registration."""
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
            'password_confirm': 'testpass123'
        }
    )
    assert response.headers['Location'] == '/auth/login'

def test_register_validation(client):
    """Test registration validation."""
    # Test password mismatch
    response = client.post(
        '/auth/register',
        data={
            'email': 'test@test.com',
            'username': 'testuser',
            'password': 'testpass123',
            'password_confirm': 'wrongpass'
        }
    )
    assert b'Passwords must match' in response.data
    
    # Test invalid email
    response = client.post(
        '/auth/register',
        data={
            'email': 'notanemail',
            'username': 'testuser',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
    )
    assert b'Invalid email address' in response.data

def test_2fa_setup(client, auth):
    """Test 2FA setup."""
    auth.login()
    
    # Test 2FA setup page loads
    response = client.get('/auth/setup-2fa')
    assert response.status_code == 200
    assert b'Setup Two-Factor Authentication' in response.data
    
    # Test 2FA activation
    response = client.post('/auth/setup-2fa', data={'code': '123456'})
    assert b'Invalid 2FA code' in response.data
