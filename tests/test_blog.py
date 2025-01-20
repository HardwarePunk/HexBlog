"""Blog functionality tests"""
import pytest
from app.models.post import Post
from app import db

@pytest.fixture
def create_test_post(app):
    with app.app_context():
        # Check if the post already exists
        existing_post = Post.query.filter_by(slug='test-post').first()
        if not existing_post:
            print('Creating test post with slug: test-post')  # Debugging statement
            post = Post(title='Test Post', content='This is a test post content.', slug='test-post', is_published=True, author_id=1)
            db.session.add(post)
            db.session.commit()
            yield post
            db.session.delete(post)
            db.session.commit()
        else:
            yield existing_post


def test_index(client):
    """Test index page shows posts."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Test Post' in response.data


def test_post_detail(client, create_test_post):
    """Test post detail page."""
    response = client.get('/post/test-post')
    assert response.status_code == 200
    assert b'Test Post' in response.data
    assert b'This is a test post content.' in response.data


def test_create_post(client, auth, app):
    """Test post creation."""
    auth.login()
    
    response = client.post('/admin/post/new', data={
        'title': 'New Test Post',
        'content': 'This is a new test post.',
        'slug': 'new-test-post',
        'is_published': True
    })
    assert response.headers['Location'].endswith('/admin/posts')
    
    with app.app_context():
        post = Post.query.filter_by(slug='new-test-post').first()
        assert post is not None
        assert post.title == 'New Test Post'


def test_edit_post(client, auth, app):
    """Test post editing."""
    auth.login()
    
    response = client.post('/admin/post/1/edit', data={
        'title': 'Updated Test Post',
        'content': 'This is an updated test post.',
        'slug': 'test-post',
        'is_published': True
    })
    assert response.headers['Location'].endswith('/admin/posts')
    
    with app.app_context():
        post = Post.query.get(1)
        assert post.title == 'Updated Test Post'
