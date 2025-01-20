from app import create_app, db
from app.models.post import Post
from app.models.user import User

app = create_app()

with app.app_context():
    # Get the first user to use as author
    author = User.query.first()
    if author:
        test_post = Post(
            title='Test Post',
            slug='test-post',
            content='This is a test post.',
            summary='Summary of test post.',
            is_published=True,
            author_id=author.id  # Set author_id
        )
        db.session.add(test_post)
        db.session.commit()
        print('Test post created with slug: test-post')
    else:
        print('No author found to assign to the test post.')
