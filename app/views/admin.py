from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app.models.post import Post
from app.models.user import User
from app import db
from functools import wraps
import os
from app.utils.upload import save_image, delete_image
from werkzeug.utils import secure_filename
import json
import logging
from flask_wtf import FlaskForm
from wtforms import BooleanField

# Rename the blueprint to avoid conflict with Flask-Admin
admin_bp = Blueprint('admin_views', __name__, url_prefix='/admin')

class RegistrationControlForm(FlaskForm):
    """Form for registration control"""
    registration_enabled = BooleanField('Allow Registration')

class UserApprovalForm(FlaskForm):
    """Form for user approval toggle"""
    pass

def admin_required(f):
    """Decorator to check if user is admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You must be an admin to access this page! >w<', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def index():
    """Admin dashboard"""
    post_count = Post.query.count()
    user_count = User.query.count()
    draft_count = Post.query.filter_by(is_published=False).count()
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    
    return render_template('admin/index.html',
                         post_count=post_count,
                         user_count=user_count,
                         draft_count=draft_count,
                         recent_posts=recent_posts)

@admin_bp.route('/posts')
@login_required
@admin_required
def posts():
    """List all posts"""
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.created_at.desc())\
        .paginate(page=page, per_page=10)
    return render_template('admin/posts.html', posts=posts)

@admin_bp.route('/post/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_post():
    """Create new post"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        summary = request.form.get('summary', '').strip()
        is_published = request.form.get('is_published') == 'true'
        
        # Validate required fields
        if not title:
            flash('Title is required! >w<', 'error')
            return render_template('admin/post_form.html', 
                                title=title, 
                                content=content, 
                                summary=summary, 
                                is_published=is_published)
            
        if not content:
            flash('Content is required! >w<', 'error')
            return render_template('admin/post_form.html', 
                                title=title, 
                                content=content, 
                                summary=summary, 
                                is_published=is_published)

        # Validate summary length
        if summary and len(summary) > 500:
            flash('Summary must be less than 500 characters! >w<', 'error')
            return render_template('admin/post_form.html',
                                title=title,
                                content=content,
                                summary=summary,
                                is_published=is_published)

        # Handle summary
        if not summary:
            # Let the model handle auto-generation
            summary = None
            
        # Create post
        post = Post(
            title=title,
            content=content,
            summary=summary,
            author=current_user,
            is_published=is_published
        )
        
        if is_published:
            post.publish()
            
        db.session.add(post)
        db.session.commit()
        
        flash('Post created successfully! 🌟', 'success')
        return redirect(url_for('admin_views.posts'))
        
    return render_template('admin/post_form.html')

@admin_bp.route('/post/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_post(id):
    """Edit existing post"""
    post = Post.query.get_or_404(id)
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        summary = request.form.get('summary', '').strip()
        original_title = request.form.get('original_title')
        is_published = request.form.get('is_published') == 'true'
        
        # Validate required fields
        if not title:
            flash('Title is required! >w<', 'error')
            return render_template('admin/post_form.html', post=post)
            
        if not content:
            flash('Content is required! >w<', 'error')
            return render_template('admin/post_form.html', post=post)

        # Validate summary length
        if summary and len(summary) > 500:
            flash('Summary must be less than 500 characters! >w<', 'error')
            return render_template('admin/post_form.html',
                                title=title,
                                content=content,
                                summary=summary,
                                is_published=is_published)

        # Handle summary
        if not summary:
            # Let the model handle auto-generation
            summary = None
            
        # Update post
        post.title = title
        post.content = content
        post.summary = summary
        
        # Generate and validate slug if title changed
        if title != original_title:
            post.slug = Post.generate_slug(title)
            if Post.query.filter(Post.id != id, Post.slug == post.slug).first():
                flash('Slug already exists! Please choose a different title! uwu', 'error')
                return render_template('admin/post_form.html', post=post)
        
        # Handle publishing state change
        if is_published and not post.is_published:
            post.publish()
        elif not is_published and post.is_published:
            post.unpublish()
            
        db.session.commit()
        flash('Post updated successfully! 🌟', 'success')
        return redirect(url_for('admin_views.posts'))
        
    return render_template('admin/post_form.html', post=post)

@admin_bp.route('/post/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_post(id):
    """Delete post"""
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully! 💫', 'success')
    return redirect(url_for('admin_views.posts'))

@admin_bp.route('/post/<int:id>/publish', methods=['POST'])
@login_required
@admin_required
def publish_post(id):
    """Publish a post"""
    post = Post.query.get_or_404(id)
    post.publish()
    db.session.commit()
    flash('Post published successfully! 🌟', 'success')
    return redirect(url_for('admin_views.posts'))

@admin_bp.route('/post/<int:id>/unpublish', methods=['POST'])
@login_required
@admin_required
def unpublish_post(id):
    """Unpublish a post"""
    post = Post.query.get_or_404(id)
    post.unpublish()
    db.session.commit()
    flash('Post unpublished successfully! 🌟', 'success')
    return redirect(url_for('admin_views.posts'))

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """List all users"""
    page = request.args.get('page', 1, type=int)
    
    # Get all non-admin users
    users = User.query.filter(~User.roles.any(name='admin'))\
        .order_by(User.created_at.desc())\
        .paginate(page=page, per_page=10)
    
    # Get registration status from current user (who is an admin)
    registration_enabled = current_user.registration_enabled
    
    # Get pending non-admin users
    pending_users = User.query.filter(
        User.is_approved.is_(False),
        ~User.roles.any(name='admin')
    ).order_by(User.created_at.desc()).all()
    
    form = RegistrationControlForm()
    approval_form = UserApprovalForm()
    
    return render_template('admin/users.html',
                         users=users,
                         registration_enabled=registration_enabled,
                         pending_users=pending_users,
                         form=form,
                         approval_form=approval_form)

@admin_bp.route('/users/toggle-registration', methods=['POST'])
@login_required
@admin_required
def toggle_registration():
    """Toggle user registration"""
    form = RegistrationControlForm()
    if form.validate_on_submit():
        enabled = request.form.get('registration_enabled') == 'on'
        
        # Update the current admin user's registration_enabled setting
        current_user.registration_enabled = enabled
        db.session.commit()
        flash('Registration settings updated successfully! ^_^', 'success')
    else:
        flash('Invalid form submission! >_<', 'error')
        return 'Bad Request: ' + str(form.errors), 400
    
    return redirect(url_for('admin_views.users'))

@admin_bp.route('/users/<int:user_id>/toggle-approval', methods=['POST'])
@login_required
@admin_required
def toggle_user_approval(user_id):
    """Toggle user approval status"""
    # Only allow toggling non-admin users
    user = User.query.filter(
        User.id == user_id,
        ~User.roles.any(name='admin')
    ).first_or_404()
    
    form = UserApprovalForm()
    if form.validate_on_submit():
        user.is_approved = not user.is_approved
        db.session.commit()
        action = 'approved' if user.is_approved else 'revoked'
        flash(f'User access has been {action}! ^_^', 'success')
    else:
        flash('Invalid form submission! >_<', 'error')
        return 'Bad Request: ' + str(form.errors), 400
    
    return redirect(url_for('admin_views.users'))

@admin_bp.route('/upload/image', methods=['POST'])
@login_required
@admin_required
def upload_image():
    """Handle image upload for Quill editor"""
    logger = logging.getLogger(__name__)
    logger.debug('Upload request received')
    logger.debug(f'Files in request: {list(request.files.keys())}')
    logger.debug(f'Form data: {list(request.form.keys())}')
    
    if 'file' not in request.files:
        logger.error('No file in request.files')
        return jsonify({'error': 'No file provided >_<'}), 400
        
    file = request.files['file']
    logger.debug(f'File info: {file.filename}, {file.content_type}')
    
    if not file:
        logger.error('Empty file object')
        return jsonify({'error': 'No file selected >w<'}), 400
        
    # Save file directly without validation for testing
    upload_folder = os.path.join(current_app.static_folder, 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(upload_folder, filename)
    
    try:
        file.save(filepath)
        image_url = url_for('static', filename=f'uploads/{filename}')
        logger.debug(f'Saved file to {filepath}, URL: {image_url}')
        return jsonify({'location': image_url})
    except Exception as e:
        logger.error(f'Error saving file: {str(e)}')
        return jsonify({'error': str(e)}), 400

@admin_bp.route('/upload-image', methods=['POST'])
@login_required
@admin_required
def upload_image_tinymce():
    """Handle image upload for TinyMCE editor"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded >_<'}), 400
        
    file = request.files['file']
    if not file:
        return jsonify({'error': 'Empty file >_<'}), 400
    
    try:
        upload_folder = os.path.join(current_app.static_folder, 'uploads')
        image_urls = save_image(file, upload_folder)
        
        # Return URL in format expected by TinyMCE
        return jsonify({
            'location': url_for('static', 
                              filename=f"uploads/{image_urls['medium']}", 
                              _external=True)
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f'Error uploading image: {e}')
        return jsonify({'error': 'Failed to upload image >_<'}), 500
