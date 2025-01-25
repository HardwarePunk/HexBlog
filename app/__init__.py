from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin
from flask_security import Security
from flask_mail import Mail
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
import os
from datetime import datetime
from sqlalchemy.orm import joinedload
from app.utils.filters import format_datetime

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
admin = Admin(template_mode='bootstrap4')
mail = Mail()
migrate = Migrate()
security = Security()

# Initialize CSRF protection
csrf = CSRFProtect()

def create_app(test_config=None):
    app = Flask(__name__, template_folder='templates')
    print('Template search paths:', app.template_folder)
    
    # Configure logging
    import logging
    logging.basicConfig(level=logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-please-change')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///blog.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECURITY_PASSWORD_SALT'] = os.getenv('SECURITY_PASSWORD_SALT', 'dev-salt-please-change')
    app.config['SECURITY_TWO_FACTOR_ENABLED'] = True
    app.config['SECURITY_TWO_FACTOR_SECRET'] = os.getenv('SECURITY_TWO_FACTOR_SECRET', 'dev-2fa-secret-please-change')
    
    # Session configuration
    app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
    
    # Override config with test config if it exists
    if test_config is not None:
        app.config.update(test_config)
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    admin.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)  # Initialize CSRF protection
    
    # Configure Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page! >_<'
    login_manager.login_message_category = 'info'
    login_manager.session_protection = 'strong'
    
    # Make sessions permanent by default
    @app.before_request
    def make_session_permanent():
        session.permanent = True
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        print(f"DEBUG: Loading user {user_id}")
        # Try loading by fs_uniquifier first
        user = User.query.options(joinedload(User.roles)).filter_by(fs_uniquifier=user_id).first()
        if not user:
            # Try loading by ID if fs_uniquifier fails
            try:
                user = User.query.options(joinedload(User.roles)).get(int(user_id))
            except (ValueError, TypeError):
                user = None
        
        if user:
            print(f"DEBUG: Found user {user.email} with roles {[role.name for role in user.roles]}")
        else:
            print(f"DEBUG: No user found for ID {user_id}")
        return user
    
    # Add template filters
    @app.template_filter('format_date')
    def format_date(value):
        """Format a datetime object into a pretty string"""
        if not value:
            return ''
        return value.strftime('%B %d, %Y')
    
    # Register datetime filter
    app.jinja_env.filters['datetime'] = format_datetime
    
    # Register blueprints
    from app.views.auth import auth_bp
    from app.views.main import main_bp
    from app.views.admin import admin_bp
    from app.views.user import user_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp)
    
    return app
