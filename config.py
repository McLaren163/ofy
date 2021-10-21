import os

CSRF_ENABLED = True
SECRET_KEY = os.urandom(16)
UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = '..\\uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
DB_PATH = 'db.sqlite'
DB_SCHEMA = 'schema.sql'
ENCODE_TYPE = 'utf-8'
MAX_CONTENT_LENGTH = 5 * 1000 * 1000
ADMIN_NAME = 'Admin'
ADMIN_EMAIL = 'admin@ofy.ru'
ADMIN_PASS = 'admin'