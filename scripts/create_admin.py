"""Script to create the initial admin user"""
import os
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from app import create_app, db
from app.models.user import User, Role
from dotenv import load_dotenv

def create_admin_user():
    """Create the initial admin user and role"""
    app = create_app()
    
    with app.app_context():
        # Check if admin role exists
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(name='admin', description='Administrator')
            db.session.add(admin_role)
        
        # Get admin credentials from environment
        admin_email = os.getenv('ADMIN_EMAIL')
        admin_password = os.getenv('ADMIN_PASSWORD')
        
        if not admin_email or not admin_password:
            print("Error: ADMIN_EMAIL and ADMIN_PASSWORD must be set in .env file")
            sys.exit(1)
        
        # Check if admin user exists
        admin_user = User.query.filter_by(email=admin_email).first()
        if admin_user:
            print(f"Admin user {admin_email} already exists!")
            return
        
        # Create admin user
        admin_user = User(
            email=admin_email,
            username='admin',
            display_name='Admin',
            active=True,
            is_approved=True,
            registration_enabled=True  # Enable registration by default
        )
        admin_user.set_password(admin_password)
        admin_user.roles.append(admin_role)
        
        db.session.add(admin_user)
        db.session.commit()
        
        print(f"Created admin user {admin_email} successfully! ✨")

if __name__ == '__main__':
    load_dotenv()
    create_admin_user()
