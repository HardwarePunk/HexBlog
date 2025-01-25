from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, URLField, HiddenField
from wtforms.validators import Optional, URL, Length

user_bp = Blueprint('user', __name__, url_prefix='/user')

class ProfileForm(FlaskForm):
    """Form for updating user profile"""
    display_name = StringField('Display Name', validators=[Optional(), Length(max=255)])
    bio = TextAreaField('Bio', validators=[Optional(), Length(max=1000)])
    website = URLField('Website', validators=[Optional(), URL()])

class DeleteAccountForm(FlaskForm):
    """Form for deleting user account"""
    pass

class DisableTwoFactorForm(FlaskForm):
    """Form for disabling 2FA"""
    pass

class BackupCodesForm(FlaskForm):
    """Form for generating backup codes"""
    pass

@user_bp.route('/settings', methods=['GET'])
@login_required
def settings():
    """User settings page"""
    profile_form = ProfileForm(obj=current_user)
    delete_form = DeleteAccountForm()
    disable_2fa_form = DisableTwoFactorForm()
    backup_codes_form = BackupCodesForm()
    
    return render_template('user/settings.html',
                         profile_form=profile_form,
                         delete_form=delete_form,
                         disable_2fa_form=disable_2fa_form,
                         backup_codes_form=backup_codes_form)

@user_bp.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    """Update user profile"""
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.display_name = form.display_name.data
        current_user.bio = form.bio.data
        current_user.website = form.website.data
        db.session.commit()
        flash('Profile updated successfully! ✨', 'success')
    else:
        flash('Invalid form submission! >_<', 'error')
    return redirect(url_for('user.settings'))

@user_bp.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    """Delete user account"""
    if current_user.has_role('admin'):
        flash('Admin accounts cannot be deleted! >_<', 'error')
        return redirect(url_for('user.settings'))
        
    # Delete user's posts
    for post in current_user.posts:
        db.session.delete(post)
    
    # Delete the user
    db.session.delete(current_user)
    db.session.commit()
    
    flash('Your account has been deleted. We hope to see you again! 👋', 'success')
    return redirect(url_for('main.index'))
