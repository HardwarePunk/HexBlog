from app import create_app, db
from app.models.user import User, Role
from app.models.post import Post

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Add database models to flask shell context"""
    return {
        'db': db,
        'User': User,
        'Role': Role,
        'Post': Post
    }

if __name__ == '__main__':
    app.run()
