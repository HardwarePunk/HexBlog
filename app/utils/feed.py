"""RSS feed generator for the blog"""
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone
from flask import url_for
import html
import re

def clean_html(content):
    """Clean HTML content for RSS feed"""
    if not content:
        return ""
    # Convert HTML to plain text (basic)
    text = re.sub(r'<[^>]+>', ' ', content)
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def generate_feed(posts, site_url):
    """Generate RSS feed from posts"""
    fg = FeedGenerator()
    fg.id(site_url)
    fg.title('Hex Blag')
    fg.description('A retro-styled blog with a modern twist')
    fg.link(href=site_url)
    fg.language('en')
    
    for post in posts:
        try:
            fe = fg.add_entry()
            fe.id(url_for('main.post_detail', slug=post.slug, _external=True))
            fe.title(post.title)
            
            # Clean and prepare content
            content = clean_html(post.content)
            summary = clean_html(post.summary) if post.summary else content[:200] + '...'
            
            fe.description(summary)
            
            # Add author info if available
            if post.author:
                fe.author(name=post.author.username)
            
            # Add timestamps, fallback to created_at if published_at is None
            published = post.published_at or post.created_at
            if published:
                fe.published(published)
            if post.updated_at:
                fe.updated(post.updated_at)
            
            # Add the link to the post
            fe.link(href=url_for('main.post_detail', slug=post.slug, _external=True))
        except Exception as e:
            # Skip problematic entries but continue generating feed
            continue
    
    return fg
