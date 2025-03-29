import os

# Configuration settings for the Flask app
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

# Allowed file extensions for upload
ALLOWED_EXTENSIONS = {'pdf'}

# Flask secret key for session management
SECRET_KEY = 'your_secret_key_here'

# Maximum file size limit (16 MB)
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

class Config:
    SECRET_KEY = "your_secret_key"
    UPLOAD_FOLDER = "uploads"
    ALLOWED_EXTENSIONS = {'pdf'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit
    