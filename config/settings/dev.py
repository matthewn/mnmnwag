from .base import *  # noqa: F401

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '=3g5ja(nplppud^1d2u%5m54w168!2g7l+yxatm$@5tdw@oact'

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*']

# print emails on console instead of sending them
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# WAGTAILADMIN_BASE_URL required for notification emails
WAGTAILADMIN_BASE_URL = 'http://localhost:8000'

# django-cachalot
CACHALOT_ENABLED = False

# django-debug-toolbar
INTERNAL_IPS = [
    '127.0.0.1',
]
