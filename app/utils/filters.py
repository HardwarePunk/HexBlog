"""Template filters for the application"""
from datetime import datetime, timezone

def format_datetime(value):
    """Format a datetime object into a string"""
    if not value:
        return ''
    
    # Convert naive datetime to UTC
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    # Convert to UTC if in a different timezone
    elif value.tzinfo != timezone.utc:
        value = value.astimezone(timezone.utc)
    
    # Get the current time in UTC
    now = datetime.now(timezone.utc)
    
    # Calculate the time difference
    diff = now - value
    
    # Format based on how long ago it was
    if diff.days == 0:
        if diff.seconds < 60:
            return 'Just now'
        elif diff.seconds < 3600:
            minutes = diff.seconds // 60
            return f'{minutes} minute{"s" if minutes != 1 else ""} ago'
        else:
            hours = diff.seconds // 3600
            return f'{hours} hour{"s" if hours != 1 else ""} ago'
    elif diff.days == 1:
        return 'Yesterday'
    elif diff.days < 7:
        return f'{diff.days} days ago'
    else:
        return value.strftime('%B %d, %Y')
