from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    test_user = User(
        email='testuser@example.com',
        username='testuser',
        password='password',
        active=True
    )
    db.session.add(test_user)
    db.session.commit()
    print('Test user created with username: testuser')
