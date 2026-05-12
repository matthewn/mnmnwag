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


# Send django.request errors to stderr so gunicorn captures tracebacks.
# Django's default console handler is gated by DEBUG=True, so without this
# unhandled 500s are silent unless ADMINS + mail_admins is configured.

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}
