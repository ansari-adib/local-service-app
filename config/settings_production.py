 
from .settings import *
import os

# ─── SECURITY SETTINGS ────────────────────────────────────────

# Never True in production
DEBUG = False

# Replace with your actual domain
ALLOWED_HOSTS = [
    'yourdomain.com',
    'www.yourdomain.com',
    'your-pythonanywhere-username.pythonanywhere.com',
]

# Secret key from environment variable
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# ─── DATABASE ─────────────────────────────────────────────────

# Switch to PostgreSQL in production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# ─── STATIC FILES ─────────────────────────────────────────────

STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = (
    'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
)

# ─── SECURITY HEADERS ─────────────────────────────────────────

# Force HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Prevent clickjacking
X_FRAME_OPTIONS = 'DENY'

# HSTS
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Content type sniffing
SECURE_CONTENT_TYPE_NOSNIFF = True

# XSS protection
SECURE_BROWSER_XSS_FILTER = True