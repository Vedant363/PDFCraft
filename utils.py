import os
from config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER

def allowed_file(filename):
    """
    Check if the uploaded file has an allowed extension.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_path(filename):
    """
    Returns the absolute path of a file in the upload directory.
    """
    return os.path.join(UPLOAD_FOLDER, filename)
