from .base import *

import os
import random
import string


DEBUG = False

# DJANGO_SECRET_KEY *should* be specified in the environment. If it's not, generate an ephemeral key.
if 'DJANGO_SECRET_KEY' in os.environ:
    SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
else:
    # Use if/else rather than a default value to avoid calculating this if we don't need it
    print("WARNING: DJANGO_SECRET_KEY not found in os.environ. Generating ephemeral SECRET_KEY.")
    SECRET_KEY = ''.join([random.SystemRandom().choice(string.printable) for i in range(50)])


# Djnago cache settings
# https://docs.djangoproject.com/en/2.2/topics/cache/

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/tmp/WAGTAIL_CACHE',
        'KEY_PREFIX': 'wagtailcache',
        'TIMEOUT': 3600,  # one hour (in seconds)
    }
}


# wagtailcache middleware entries

MIDDLEWARE.insert(0, 'wagtailcache.cache.UpdateCacheMiddleware')  # noqa: 405
MIDDLEWARE.append('wagtailcache.cache.FetchFromCacheMiddleware')  # noqa: 405
