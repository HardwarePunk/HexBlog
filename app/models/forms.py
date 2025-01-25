"""Forms for models"""
from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms.validators import DataRequired, Length

class CommentForm(FlaskForm):
    """Form for adding comments"""
    content = TextAreaField('Comment', validators=[
        DataRequired(message='Comment cannot be empty >_<'),
        Length(min=1, max=1000, message='Comment must be between 1 and 1000 characters >_<')
    ])
