# Hex Blag

A geocities-inspired blog platform built with Flask, featuring:
- Secure authentication with 2FA
- WYSIWYG editor for posts
- Retro-styled interface
- Admin dashboard
- Image upload support

## ✨ Features

### Security & Authentication
- 🔒 Secure user authentication with password hashing
- 🔑 Two-factor authentication (2FA) support
- 🛡️ CSRF protection and rate limiting
- 👥 Admin approval system for new accounts

### Content Management
- 📝 WYSIWYG editor for posts with Markdown support
- 📸 Image upload and management
- 📋 Automatic post summary generation
- 🏷️ Automatic SEO-friendly slug generation
- 📦 Draft post support with publishing workflow

### Community Features
- 💬 Commenting system with moderation
- 👤 User profiles
- 🎨 Retro-styled interface with consistent theming
- 📱 Mobile-responsive design

### Admin Features
- 🎛️ Admin dashboard for content management
- 👥 User management with approval controls
- 📊 Post analytics (views, comments)
- 🔍 Content moderation tools

## Setup

### Option 1: Local Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy the example environment file:
```bash
cp .env.example .env
# Edit .env with your settings
```

4. Initialize the database:
```bash
flask db upgrade
```

5. Create the admin user:
```bash
python scripts/create_admin.py
```

6. Run the development server:
```bash
flask run
```

### Option 2: Docker Setup

1. Build and start the containers:
```bash
docker-compose up --build
```

The application will be available at `http://localhost:5000`

## Project Structure

```
/app
  ├── templates/    # Jinja2 templates
  ├── static/       # CSS, JS, images
  ├── models/       # Database models
  ├── views/        # Route handlers
  ├── auth/         # Authentication logic
  └── scripts/      # Utility scripts for testing and database management
```

## Scripts Directory

The `scripts` directory contains various utility scripts used for testing and database management. These scripts include:
- `check_post.py`: Check for the existence of posts in the database.
- `create_post_table.py`: Create the post table in the database.
- `create_test_post.py`: Create a test post in the database.
- `create_test_user.py`: Create a test user in the database.
- `get_author.py`: Retrieve the author details from the database.
- `list_posts.py`: List all posts in the database.
- `verify_user.py`: Verify the existence of a specific user in the database.

## Testing

### Running Tests Locally
```bash
pytest -v
```

### Running Tests with Docker
```bash
docker-compose run test
```

The test suite includes:
- Authentication tests (login, logout)
- Blog functionality tests (viewing, creating, editing posts)
- Admin interface tests

For more detailed test output:
```bash
pytest -v
```

To see test coverage:
```bash
pytest --cov=app tests/
```
