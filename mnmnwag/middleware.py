from django.core.cache import cache
from django.http import HttpResponse
from django.utils.cache import patch_vary_headers

LIKES_RATE_LIMIT = 10  # max likes per IP per hour


class LikesGuardMiddleware:
    """
    Guard /likes/ requests:
    - Reject sessions that have not viewed a blog page.
    - Rate-limit by IP address to LIKES_RATE_LIMIT requests per hour.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/likes/'):
            if not request.session.get('has_viewed_blog'):
                return HttpResponse('Forbidden', status=403)
            ip = request.META.get('REMOTE_ADDR', '')
            cache_key = f'likes_rl:{ip}'
            cache.add(cache_key, 0, 3600)
            count = cache.incr(cache_key)
            if count > LIKES_RATE_LIMIT:
                return HttpResponse('Too Many Requests', status=429)
        return self.get_response(request)


class ThemeClassCacheMiddleware:
    """
    Normalize the themeClass cookie into a request header so that
    wagtailcache can vary its cache keys on theme without varying on
    all cookies (which would make caching useless).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        theme = request.COOKIES.get('themeClass', 'theme-light')
        request.META['HTTP_X_THEME_CLASS'] = theme

        response = self.get_response(request)
        patch_vary_headers(response, ['X-Theme-Class'])
        return response
