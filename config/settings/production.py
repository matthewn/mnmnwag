from .base import *  # noqa: 401

DEBUG = False


# Django cache settings
# https://docs.djangoproject.com/en/5.2/topics/cache/

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'KEY_PREFIX': 'wagtailcache',
        'TIMEOUT': 900,  # 15 minutes (in seconds)
    }
}


# wagtailcache middleware entries

MIDDLEWARE.insert(0, 'wagtailcache.cache.UpdateCacheMiddleware')  # noqa: F405
MIDDLEWARE.insert(1, 'mnmnwag.middleware.ThemeClassCacheMiddleware')  # noqa: F405
MIDDLEWARE.append('wagtailcache.cache.FetchFromCacheMiddleware')  # noqa: F405
