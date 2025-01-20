from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    user = User.query.filter_by(username='testuser').first()  # Check for the test user
    if user:
        print(f'User found: {user.username}, Email: {user.email}')
    else:
        print('Test user not found.')
