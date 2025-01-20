from app import db
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property
import re

class Post(db.Model):
    """Blog post model with support for drafts and rich content"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.String(500))
    
    # Post status
    is_published = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    
    # Metadata
    meta_description = db.Column(db.String(160))
    meta_keywords = db.Column(db.String(255))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __init__(self, *args, **kwargs):
        is_published = kwargs.pop('is_published', False)
        super().__init__(*args, **kwargs)
        if is_published:
            self.published_at = datetime.utcnow()
            
    def __str__(self):
        return f'<Post {self.title}>'
    
    @hybrid_property
    def reading_time(self):
        """Estimate reading time in minutes"""
        words = len(re.findall(r'\w+', self.content))
        minutes = words / 200  # Average reading speed
        return round(minutes)
    
    @classmethod
    def generate_slug(cls, title):
        """Generate URL-friendly slug from title"""
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[-\s]+', '-', slug).strip('-')
        base_slug = slug
        counter = 1
        
        # Ensure unique slug
        while cls.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
            
        return slug
    
    def publish(self):
        """Publish the post"""
        self.is_published = True
        self.published_at = datetime.utcnow()
        
    def unpublish(self):
        """Unpublish the post"""
        self.is_published = False
        self.published_at = None
