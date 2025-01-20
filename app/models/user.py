from app import db
from flask_security import UserMixin, RoleMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import qrcode
import base64
from io import BytesIO
import pyotp

# Role-User association table for Flask-Security
roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    """Role model for user permissions"""
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    """User model with 2FA support"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean(), default=True)
    confirmed_at = db.Column(db.DateTime())
    
    # Two-factor auth
    tf_phone_number = db.Column(db.String(128))
    tf_primary_method = db.Column(db.String(64))
    tf_totp_secret = db.Column(db.String(255))
    
    # Profile fields
    display_name = db.Column(db.String(255))
    bio = db.Column(db.Text)
    avatar_url = db.Column(db.String(255))
    website = db.Column(db.String(255))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    roles = db.relationship('Role', secondary=roles_users,
                          backref=db.backref('users', lazy='dynamic'))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    # Add fs_uniquifier attribute
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))

    def __str__(self):
        return f'<User {self.email}>'

    @property
    def is_admin(self):
        """Check if user has admin role"""
        roles = list(self.roles)  # Force load roles
        print(f"DEBUG: User {self.email} has roles: {[role.name for role in roles]}")
        return any(role.name == 'admin' for role in roles)

    def set_password(self, password):
        """Set password hash for user"""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Check if password matches hash"""
        return check_password_hash(self.password, password)

    def get_2fa_qr_code(self):
        """Generate QR code for 2FA setup"""
        if not self.tf_totp_secret:
            return None
            
        totp = pyotp.TOTP(self.tf_totp_secret)
        provisioning_uri = totp.provisioning_uri(
            self.email,
            issuer_name='Retro Blog'
        )
        
        img = qrcode.make(provisioning_uri)
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
