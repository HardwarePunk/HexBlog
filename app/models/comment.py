"""Comment model for blog posts"""
from datetime import datetime, timezone
from app import db

class Comment(db.Model):
    """Comment model"""
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, onupdate=lambda: datetime.now(timezone.utc))
    
    # Foreign keys
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    
    # Relationships
    post = db.relationship('Post', back_populates='comments')
    author = db.relationship('User', back_populates='comments')
    
    def __repr__(self):
        """String representation"""
        return f'<Comment by {self.author.username} on post {self.post.title}>'
