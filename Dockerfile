FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Install the application in development mode
RUN pip install -e .

# Set environment variables
ENV FLASK_APP=wsgi.py
ENV FLASK_ENV=development
ENV PYTHONPATH=/app

# Run tests by default
CMD ["pytest", "-v"]
