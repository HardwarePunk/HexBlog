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
