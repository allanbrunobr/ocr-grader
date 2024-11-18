import os

UPLOAD_HTML = 'upload.html'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './credentials/credentials.json'
