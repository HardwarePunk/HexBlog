from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from app.models.post import Post
from app.models.comment import Comment
from app.models.user import User
from app.models.forms import CommentForm
from app import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page with list of blog posts"""
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter(
        Post.is_published == True,
        Post.published_at.isnot(None)
    ).order_by(Post.published_at.desc())\
        .paginate(page=page, per_page=5)
    return render_template('main/index.html', posts=posts)

@main_bp.route('/post/<string:slug>')
def post_detail(slug):
    """Individual blog post page"""
    # Only show published posts
    post = Post.query.filter(
        Post.slug == slug,
        Post.is_published == True,
        Post.published_at.isnot(None)
    ).first_or_404()
    comment_form = CommentForm()
    return render_template('main/post.html', post=post, comment_form=comment_form)

@main_bp.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    """Add a comment to a post"""
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    
    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            post=post,
            author=current_user
        )
        db.session.add(comment)
        db.session.commit()
        flash('Comment added successfully! ✨', 'success')
    else:
        flash('Invalid comment! >_<', 'error')
    
    return redirect(url_for('main.post_detail', slug=post.slug))

@main_bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    """Delete a comment"""
    comment = Comment.query.get_or_404(comment_id)
    
    if comment.author != current_user:
        flash('You can only delete your own comments! >_<', 'error')
        return redirect(url_for('main.post_detail', slug=comment.post.slug))
    
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted successfully! ✨', 'success')
    
    return redirect(url_for('main.post_detail', slug=comment.post.slug))

@main_bp.route('/about')
def about():
    """About page"""
    return render_template('main/about.html')

@main_bp.route('/search')
def search():
    """Search for blog posts"""
    query = request.args.get('q', '').strip()
    if not query:
        flash('Please enter a search term! uwu', 'info')
        return redirect(url_for('main.index'))
        
    posts = Post.query.filter(
        Post.is_published == True,  # Only show published posts
        Post.published_at.isnot(None),  # Only show posts with published_at date
        (Post.title.ilike(f'%{query}%') |  # Search in title
         Post.content.ilike(f'%{query}%'))  # Search in content
    ).order_by(Post.published_at.desc()).all()
    
    return render_template('main/search.html', posts=posts, query=query)

@main_bp.app_template_filter('format_date')
def format_date(date, format='%B %d, %Y'):
    """Template filter for formatting dates"""
    return date.strftime(format) if date else ''
