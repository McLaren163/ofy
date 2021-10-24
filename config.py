import os

CSRF_ENABLED = True
SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(16)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
DB_PATH = 'db.sqlite'
DB_SCHEMA = 'schema.sql'
ENCODE_TYPE = 'utf-8'
MAX_CONTENT_LENGTH = 5 * 1000 * 1000
ADMIN_NAME = os.environ.get('ADMIN_NAME') or 'Admin'
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'admin@ofy.ru'
ADMIN_PASS = os.environ.get('ADMIN_PASS') or 'admin'
