from flask import Blueprint, render_template, request, current_app
from app.models.post import Post
from app.models.user import User

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page with list of blog posts"""
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(is_published=True)\
        .order_by(Post.published_at.desc())\
        .paginate(page=page, per_page=5)
    return render_template('main/index.html', posts=posts)

@main_bp.route('/post/<string:slug>')
def post(slug):
    """Individual blog post page"""
    post = Post.query.filter_by(slug=slug, is_published=True).first_or_404()
    return render_template('main/post.html', post=post)

@main_bp.route('/about')
def about():
    """About page"""
    return render_template('main/about.html')

@main_bp.app_template_filter('format_date')
def format_date(date, format='%B %d, %Y'):
    """Template filter for formatting dates"""
    return date.strftime(format) if date else ''
