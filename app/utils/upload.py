import os
from werkzeug.utils import secure_filename
from PIL import Image
import magic
import uuid

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_image(file):
    """Validate file is actually an image and not too large"""
    # Check file size
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    
    if size > MAX_FILE_SIZE:
        return False, "File size too large (max 5MB)"
    
    # Check file type using python-magic
    mime = magic.from_buffer(file.read(2048), mime=True)
    file.seek(0)
    
    if not mime.startswith('image/'):
        return False, "File is not an image"
        
    return True, None

def save_image(file, upload_folder):
    """Save uploaded image with validation"""
    import logging
    logger = logging.getLogger(__name__)
    
    if not file:
        logger.error('No file provided')
        return None, "No file provided"
        
    if not allowed_file(file.filename):
        logger.error(f'File type not allowed: {file.filename}')
        return None, "File type not allowed"
        
    is_valid, error = validate_image(file)
    if not is_valid:
        logger.error(f'Image validation failed: {error}')
        return None, error
        
    # Generate unique filename
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{str(uuid.uuid4())}.{ext}"
    
    # Create upload folder if it doesn't exist
    os.makedirs(upload_folder, exist_ok=True)
    
    filepath = os.path.join(upload_folder, filename)
    logger.debug(f'Saving file to: {filepath}')
    
    # Save and optimize image
    try:
        with Image.open(file) as img:
            # Convert RGBA to RGB if PNG
            if img.mode == 'RGBA':
                logger.debug('Converting RGBA to RGB')
                img = img.convert('RGB')
            # Save with optimization
            logger.debug('Saving optimized image')
            img.save(filepath, optimize=True, quality=85)
    except Exception as e:
        logger.error(f'Error saving image: {str(e)}')
        return None, f"Error saving image: {str(e)}"
        
    logger.debug(f'Successfully saved image: {filename}')
    return filename, None

def delete_image(filename, upload_folder):
    """Delete image file"""
    if not filename:
        return
        
    filepath = os.path.join(upload_folder, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
