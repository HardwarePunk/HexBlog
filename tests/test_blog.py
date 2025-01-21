"""Blog functionality tests"""
import pytest
from app.models.post import Post
from app import db, create_app

app = create_app()

@pytest.fixture
def create_test_post(app):
    with app.app_context():
        # Check if the post already exists
        existing_post = Post.query.filter_by(slug='test-post').first()
        if not existing_post:
            print('Creating test post with slug: test-post')  # Debugging statement
            post = Post(title='Test Post', content='This is a test post content.', slug='test-post', is_published=True, author_id=1)
            post.publish()  # This will set published_at
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
        'is_published': 'true'
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
        'is_published': 'true'
    })
    assert response.headers['Location'].endswith('/admin/posts')
    
    with app.app_context():
        post = Post.query.get(1)
        assert post.title == 'Updated Test Post'


def test_create_post_validation(client, auth, create_test_post, app):
    """Test post creation validation."""
    auth.login()
    
    # Test empty title
    response = client.post('/admin/post/new', data={
        'title': '',
        'content': 'Test content',
        'slug': 'test-slug',
        'is_published': 'true'
    })
    assert b'Title is required' in response.data
    
    # Test automatic unique slug generation
    response = client.post('/admin/post/new', data={
        'title': 'Test Post',  # This will generate a unique slug
        'content': 'This is another test post.',
        'is_published': 'true'
    })
    assert response.headers['Location'].endswith('/admin/posts')
    
    # Verify the post was created with a unique slug
    with app.app_context():
        post = Post.query.filter_by(title='Test Post').order_by(Post.id.desc()).first()
        assert post is not None
        assert post.slug == 'test-post-1'  # Should have -1 appended


def test_delete_post(client, auth, app, create_test_post):
    """Test post deletion."""
    auth.login()
    
    response = client.post('/admin/post/1/delete')
    assert response.headers['Location'].endswith('/admin/posts')
    
    with app.app_context():
        post = Post.query.get(1)
        assert post is None


def test_draft_post(client, auth, app):
    """Test draft post functionality."""
    auth.login()
    
    # Create draft post
    response = client.post('/admin/post/new', data={
        'title': 'Draft Post',
        'content': 'This is a draft post.',
        'slug': 'draft-post',
        'is_published': 'false'
    })
    assert response.headers['Location'].endswith('/admin/posts')
    
    # Verify draft post not visible on main page
    response = client.get('/')
    assert b'Draft Post' not in response.data
    
    # Verify draft post visible in admin
    response = client.get('/admin/posts')
    assert b'Draft Post' in response.data


def test_post_search(client, create_test_post):
    """Test post search functionality."""
    # Test successful search
    response = client.get('/search?q=test')
    assert response.status_code == 200
    assert b'Test Post' in response.data
    
    # Test empty search
    response = client.get('/search?q=nonexistent')
    assert response.status_code == 200
    assert b'No posts found' in response.data


def test_post_summary(client, auth, app):
    """Test post summary functionality."""
    auth.login()
    
    with app.app_context():
        # Test creating post with summary
        response = client.post('/admin/post/new', data={
            'title': 'Post With Summary',
            'content': 'This is a very long post content that should not appear in the preview.',
            'summary': 'This is a custom summary!',
            'is_published': 'true'
        })
        assert response.headers['Location'].endswith('/admin/posts')
        
        # Verify post was created with summary
        post = Post.query.filter_by(title='Post With Summary').first()
        assert post is not None
        assert post.summary == 'This is a custom summary!'
        
        # Verify summary appears on homepage
        response = client.get('/')
        assert b'This is a custom summary!' in response.data
        
        # Test creating post without summary (should auto-generate)
        content = 'This is another post without an explicit summary. It should use the first part of the content.'
        response = client.post('/admin/post/new', data={
            'title': 'Post Without Summary',
            'content': content,
            'is_published': 'true'
        })
        assert response.headers['Location'].endswith('/admin/posts')
        
        # Verify auto-generated summary
        post = Post.query.filter_by(title='Post Without Summary').first()
        assert post is not None
        assert post.summary == content  # Content is short enough to use as-is
        
        # Test summary length validation
        long_summary = 'x' * 501  # Create summary > 500 chars
        response = client.post('/admin/post/new', data={
            'title': 'Post With Long Summary',
            'content': 'Some content',
            'summary': long_summary,
            'is_published': 'true'
        })
        assert b'Summary must be less than 500 characters' in response.data


def test_edit_post_summary(client, auth, app, create_test_post):
    """Test editing post summary."""
    auth.login()
    
    # Edit post to add summary
    response = client.post('/admin/post/1/edit', data={
        'title': 'Test Post',
        'content': create_test_post.content,
        'summary': 'New awesome summary!',
        'is_published': 'true',
        'original_title': 'Test Post'
    })
    assert response.headers['Location'].endswith('/admin/posts')
    
    # Verify summary appears on homepage
    response = client.get('/')
    assert b'New awesome summary!' in response.data
    
    # Test updating with invalid summary length
    long_summary = 'x' * 501
    response = client.post('/admin/post/1/edit', data={
        'title': 'Test Post',
        'content': create_test_post.content,
        'summary': long_summary,
        'is_published': 'true',
        'original_title': 'Test Post'
    })
    assert b'Summary must be less than 500 characters' in response.data
