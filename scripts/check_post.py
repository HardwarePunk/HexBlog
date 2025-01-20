from app import create_app, db
from app.models.post import Post

app = create_app()

with app.app_context():
    post = Post.query.filter_by(slug='test-post').first()
    print(post)
