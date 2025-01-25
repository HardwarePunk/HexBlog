"""Test URL routing"""
import pytest
from flask import url_for

def test_main_routes(client):
    """Test that all main routes are accessible"""
    routes = [
        ('main.index', {}),
        ('main.about', {}),
        ('main.post_detail', {'slug': 'test-post'}),
    ]
    
    for endpoint, kwargs in routes:
        url = url_for(endpoint, **kwargs)
        assert url is not None

def test_admin_routes(client):
    """Test that all admin routes are accessible"""
    routes = [
        ('admin_views.index', {}),
        ('admin_views.posts', {}),
        ('admin_views.new_post', {}),
        ('admin_views.edit_post', {'id': 1}),
    ]
    
    for endpoint, kwargs in routes:
        url = url_for(endpoint, **kwargs)
        assert url is not None

def test_auth_routes(client):
    """Test that all auth routes are accessible"""
    routes = [
        ('auth.login', {}),
        ('auth.register', {}),
        ('auth.logout', {}),
        ('auth.setup_2fa', {}),
        ('auth.generate_backup_codes_route', {}),
    ]
    
    for endpoint, kwargs in routes:
        url = url_for(endpoint, **kwargs)
        assert url is not None

def test_user_routes(client):
    """Test that all user routes are accessible"""
    routes = [
        ('user.settings', {}),
    ]
    
    for endpoint, kwargs in routes:
        url = url_for(endpoint, **kwargs)
        assert url is not None
