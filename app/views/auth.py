from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User, Role
from app import db
from sqlalchemy.orm import joinedload
import pyotp
from datetime import datetime
import qrcode
import base64
from io import BytesIO
import secrets

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def generate_backup_codes(n=8):
    """Generate n backup codes"""
    return [secrets.token_hex(4).upper() for _ in range(n)]

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login with 2FA"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if not user.is_approved:
                flash('Your account is pending approval >_<', 'error')
                return render_template('auth/login.html')
                
            if user.tf_enabled:
                # Store user ID in session for 2FA
                session['_2fa_user_id'] = user.id
                return redirect(url_for('auth.two_factor'))
            
            login_user(user)
            flash('Welcome back! ✨', 'success')
            return redirect(url_for('main.index'))
            
        flash('Invalid email or password >_<', 'error')
    return render_template('auth/login.html')

@auth_bp.route('/two-factor', methods=['GET', 'POST'])
def two_factor():
    """Handle 2FA verification"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    user_id = session.get('_2fa_user_id')
    if not user_id:
        return redirect(url_for('auth.login'))
        
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for('auth.login'))
        
    if request.method == 'POST':
        code = request.form.get('code')
        totp = pyotp.TOTP(user.tf_totp_secret)
        
        # Check TOTP code or backup codes
        if totp.verify(code) or code in (user.backup_codes or []):
            if code in (user.backup_codes or []):
                # Remove used backup code
                user.backup_codes.remove(code)
                db.session.commit()
                
            login_user(user)
            session.pop('_2fa_user_id', None)
            flash('Welcome back! ✨', 'success')
            return redirect(url_for('main.index'))
            
        flash('Invalid authentication code >_<', 'error')
    return render_template('auth/two_factor.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # Check if registration is enabled by checking any admin user's setting
    admin = User.query.join(User.roles).filter(Role.name == 'admin').first()
    if not admin or not admin.registration_enabled:
        flash('Registration is currently disabled! >_<', 'error')
        return redirect(url_for('auth.login'))
        
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password')
        password_confirm = request.form.get('confirm_password')
        
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
        
        # Check if this is the first user (make them admin)
        if User.query.count() == 0:
            admin_role = Role.query.filter_by(name='admin').first()
            if not admin_role:
                admin_role = Role(name='admin', description='Administrator')
                db.session.add(admin_role)
            user.roles.append(admin_role)
            user.is_approved = True
            user.registration_enabled = True
        else:
            user.is_approved = False  # New users start unapproved
        
        db.session.add(user)
        db.session.commit()
        
        if user.has_role('admin'):
            flash('Admin account created successfully! ✨', 'success')
        else:
            flash('Registration successful! Please wait for admin approval before logging in! ✨', 'success')
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
        
        # Generate backup codes
        backup_codes = generate_backup_codes()
        current_user.backup_codes = backup_codes
        current_user.tf_enabled = True
        db.session.commit()
        
        flash('2FA enabled successfully! ✨ Here are your backup codes - keep them safe!', 'success')
        return render_template('auth/backup_codes.html', backup_codes=backup_codes)
    
    # Generate new TOTP secret if not exists
    if not current_user.tf_totp_secret:
        current_user.tf_totp_secret = pyotp.random_base32()
        db.session.commit()
    
    # Generate QR code
    totp = pyotp.TOTP(current_user.tf_totp_secret)
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    provisioning_uri = totp.provisioning_uri(
        current_user.email,
        issuer_name="Hex's Blog"
    )
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered)
    qr_code = base64.b64encode(buffered.getvalue()).decode()
    
    return render_template('auth/setup_2fa.html', qr_code=qr_code)

@auth_bp.route('/disable-2fa', methods=['POST'])
@login_required
def disable_2fa():
    """Disable 2FA for user"""
    current_user.tf_enabled = False
    current_user.tf_totp_secret = None
    current_user.backup_codes = None
    db.session.commit()
    flash('2FA has been disabled! >_<', 'success')
    return redirect(url_for('user.settings'))

@auth_bp.route('/recovery', methods=['GET', 'POST'])
def recovery():
    """Handle account recovery with backup codes"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    user_id = session.get('_2fa_user_id')
    if not user_id:
        return redirect(url_for('auth.login'))
        
    if request.method == 'POST':
        code = request.form.get('code')
        user = User.query.get(user_id)
        
        if not user or not user.backup_codes or code not in user.backup_codes:
            flash('Invalid backup code >_<', 'error')
            return render_template('auth/recovery.html')
            
        # Remove used backup code
        user.backup_codes.remove(code)
        db.session.commit()
        
        login_user(user)
        session.pop('_2fa_user_id', None)
        flash('Welcome back! Consider generating new backup codes in settings ✨', 'success')
        return redirect(url_for('main.index'))
        
    return render_template('auth/recovery.html')

@auth_bp.route('/generate-backup-codes', methods=['POST'])
@login_required
def generate_backup_codes_route():
    """Generate new backup codes for user"""
    if not current_user.tf_enabled:
        flash('2FA must be enabled to generate backup codes! >_<', 'error')
        return redirect(url_for('user.settings'))
    
    backup_codes = generate_backup_codes()
    current_user.backup_codes = backup_codes
    db.session.commit()
    
    flash('New backup codes generated! ✨', 'success')
    return render_template('auth/backup_codes.html', backup_codes=backup_codes)

@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout"""
    print(f"DEBUG: Logging out user {current_user.email}")
    logout_user()
    session.clear()  # Clear all session data
    flash('You have been logged out! Come back soon~ ✨', 'info')
    return redirect(url_for('main.index'))
