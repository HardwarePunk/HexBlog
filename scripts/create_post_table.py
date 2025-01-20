from app import create_app, db
from app.models.post import Post

app = create_app()

with app.app_context():
    db.create_all()  # This will create all tables defined in the models
    print('Post table created if it did not exist.')
