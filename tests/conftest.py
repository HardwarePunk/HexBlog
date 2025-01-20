"""Test configuration and fixtures"""
import os
import sys
import tempfile
import pytest
from pathlib import Path
from datetime import datetime

# Add the parent directory to Python path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app, db
from app.models.user import User, Role
from app.models.post import Post

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'WTF_CSRF_ENABLED': False,
        'SECURITY_PASSWORD_SALT': 'test-salt',
        'SECRET_KEY': 'test-key'
    })

    # Create the database and load test data
    with app.app_context():
        db.create_all()
        
        # Create test role
        admin_role = Role(name='admin', description='Administrator')
        db.session.add(admin_role)
        
        # Create test admin user
        admin = User(
            email='admin@test.com',
            username='admin',
            display_name='Test Admin',
            active=True
        )
        admin.set_password('password123')
        admin.roles.append(admin_role)
        db.session.add(admin)
        
        # Create test blog post
        post = Post(
            title='Test Post',
            content='This is a test post content.',
            slug='test-post',
            is_published=True,
            author=admin
        )
        post.publish()  # This will set published_at
        db.session.add(post)
        
        db.session.commit()

    yield app

    # Close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()

@pytest.fixture
def auth(client):
    """Authentication helper for tests."""
    class AuthActions:
        def __init__(self, client):
            self._client = client

        def login(self, email='admin@test.com', password='password123'):
            return self._client.post('/auth/login', data={
                'email': email,
                'password': password,
                'csrf_token': self._client.get('/auth/login').data.decode('utf-8').split('name="csrf_token" value="')[1].split('"')[0]
            })

        def logout(self):
            return self._client.get('/auth/logout')

    return AuthActions(client)

@pytest.fixture
def create_test_user(app):
    with app.app_context():
        user = User(email='admin@test.com', username='admin', password='password123')
        user.set_password('password123')  # Set the password hash
        db.session.add(user)
        db.session.commit()
        yield user
        db.session.delete(user)
        db.session.commit()
