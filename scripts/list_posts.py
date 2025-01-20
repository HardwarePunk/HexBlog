from app import create_app, db
from app.models.post import Post

app = create_app()

with app.app_context():
    posts = Post.query.all()
    for post in posts:
        print(f'Post Title: {post.title}, Slug: {post.slug}')
