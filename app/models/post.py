from app import db
from datetime import datetime, timezone
from sqlalchemy.ext.hybrid import hybrid_property
import re

class Post(db.Model):
    """Blog post model with support for drafts and rich content"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    _summary = db.Column('summary', db.String(500))
    
    # Post status
    is_published = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    
    # Metadata
    meta_description = db.Column(db.String(160))
    meta_keywords = db.Column(db.String(255))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    published_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', back_populates='posts')
    comments = db.relationship('Comment', back_populates='post', cascade='all, delete-orphan')
    
    def __init__(self, *args, **kwargs):
        is_published = kwargs.pop('is_published', False)
        super().__init__(*args, **kwargs)
        if is_published:
            self.published_at = datetime.now(timezone.utc)
            
    def __str__(self):
        return f'<Post {self.title}>'
    
    def __repr__(self):
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
        if not self.published_at:  # Only set published_at if not already set
            self.published_at = datetime.now(timezone.utc)
        
    def unpublish(self):
        """Unpublish the post"""
        self.is_published = False
        self.published_at = None

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        """Set the summary, auto-generating if not provided"""
        if value:
            self._summary = value
        else:
            # Auto-generate summary from content
            if len(self.content) > 200:
                self._summary = self.content[:197] + '...'
            else:
                self._summary = self.content
