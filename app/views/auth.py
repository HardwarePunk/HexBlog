from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app import db
from sqlalchemy.orm import joinedload
import pyotp
from datetime import datetime
import qrcode
import base64
from io import BytesIO

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login with 2FA"""
    print(f"DEBUG: Current user authenticated? {current_user.is_authenticated}")
    
    if current_user.is_authenticated:
        print(f"DEBUG: User already logged in as {current_user.email}")
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))
        
        print(f"DEBUG: Login attempt for {email}")
        
        # Use joinedload to load roles relationship
        user = User.query.options(joinedload(User.roles)).filter_by(email=email).first()
        
        if user and user.check_password(password):
            if user.tf_totp_secret:  # 2FA is enabled
                session['temp_user_id'] = user.id
                session['remember'] = remember
                print(f"DEBUG: 2FA required for {email}")
                return redirect(url_for('auth.two_factor'))
            
            # No 2FA, log in directly
            login_user(user, remember=remember)
            print(f"DEBUG: Successfully logged in {email} with roles {[role.name for role in user.roles]}")
            session.permanent = True  # Make this session permanent
            session['user_id'] = user.fs_uniquifier  # Store user's fs_uniquifier in session
            session['_fresh'] = True  # Mark session as fresh
            flash('Welcome back! ✨', 'success')
            return redirect(url_for('main.index'))
        else:
            print(f"DEBUG: Login failed for {email}")
            flash('Invalid email or password >_<', 'error')
        
    return render_template('auth/login.html')

@auth_bp.route('/two-factor', methods=['GET', 'POST'])
def two_factor():
    """Handle 2FA verification"""
    if 'temp_user_id' not in session:
        return redirect(url_for('auth.login'))
        
    # Use joinedload to load roles relationship
    user = User.query.options(joinedload(User.roles)).get(session['temp_user_id'])
    
    if request.method == 'POST':
        code = request.form.get('code')
        totp = pyotp.TOTP(user.tf_totp_secret)
        
        if totp.verify(code):
            login_user(user, remember=session.get('remember', False))
            session.pop('temp_user_id')
            session.pop('remember', None)
            flash('Successfully verified! Welcome back! ✨', 'success')
            return redirect(url_for('main.index'))
            
        flash('Invalid 2FA code >_<', 'error')
    
    return render_template('auth/two_factor.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        # Validate email format
        if '@' not in email or '.' not in email:
            flash('Invalid email address! >w<', 'error')
            return render_template('auth/register.html')
        
        # Validate passwords match
        if password != password_confirm:
            flash('Passwords must match! >w<', 'error')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered >_<', 'error')
            return render_template('auth/register.html')
            
        if User.query.filter_by(username=username).first():
            flash('Username already taken >_<', 'error')
            return render_template('auth/register.html')
        
        user = User(email=email, username=username)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Welcome aboard! ✨', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')

@auth_bp.route('/setup-2fa', methods=['GET', 'POST'])
@login_required
def setup_2fa():
    """Set up 2FA for user"""
    if request.method == 'POST':
        code = request.form.get('code')
        totp = pyotp.TOTP(current_user.tf_totp_secret)
        
        if not totp.verify(code):
            flash('Invalid 2FA code >_<', 'error')
            return render_template('auth/setup_2fa.html', qr_code=current_user.get_2fa_qr_code())
        
        current_user.tf_enabled = True
        db.session.commit()
        flash('2FA enabled successfully! ✨', 'success')
        return redirect(url_for('main.index'))
    
    # Generate new TOTP secret if not exists
    if not current_user.tf_totp_secret:
        current_user.tf_totp_secret = pyotp.random_base32()
        db.session.commit()
    
    return render_template('auth/setup_2fa.html', qr_code=current_user.get_2fa_qr_code())

@auth_bp.route('/disable-2fa', methods=['POST'])
@login_required
def disable_2fa():
    """Disable 2FA for user"""
    if not current_user.tf_totp_secret:
        flash('2FA is not enabled! >w<', 'error')
        return redirect(url_for('main.index'))
        
    current_user.tf_totp_secret = None
    db.session.commit()
    flash('2FA has been disabled! Stay safe! ✨', 'success')
    return redirect(url_for('main.index'))

@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout"""
    print(f"DEBUG: Logging out user {current_user.email}")
    logout_user()
    session.clear()  # Clear all session data
    flash('You have been logged out! Come back soon~ ✨', 'info')
    return redirect(url_for('main.index'))
