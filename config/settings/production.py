from .base import *

DEBUG = False


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
