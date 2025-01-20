from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    user = User.query.first()  # Get the first user
    print(user.id if user else 'No users found.')
