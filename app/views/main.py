from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for
from app.models.post import Post
from app.models.user import User

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
def post(slug):
    """Individual blog post page"""
    # Only show published posts
    post = Post.query.filter(
        Post.slug == slug,
        Post.is_published == True,
        Post.published_at.isnot(None)
    ).first_or_404()
    return render_template('main/post.html', post=post)

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
