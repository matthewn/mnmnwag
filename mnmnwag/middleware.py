import re
from hashlib import md5

from django.core.cache import cache
from django.http import HttpResponse
from django.utils.cache import patch_vary_headers

from likes.middleware import SecretBallotUserIpUseragentMiddleware

from .utils import get_client_ip

LIKES_RATE_LIMIT = 10  # max likes per IP per hour

# Version numbers turn every browser update into a new voter; what survives the
# strip still separates browser, OS and form factor.
VERSION_NUMBERS = re.compile(r'[\d.]+')


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
            ip = get_client_ip(request)
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


class SecretBallotClientIpUseragentMiddleware(SecretBallotUserIpUseragentMiddleware):
    """
    Identify a voter by client IP plus a version-stripped user agent.

    The parent builds its token from REMOTE_ADDR, which is empty behind
    gunicorn on a unix socket -- leaving the user agent as the only thing
    telling voters apart, so strangers sharing a browser also shared a vote.
    """

    def generate_token(self, request):
        if request.user.is_authenticated:
            return request.user.username
        ip = get_client_ip(request)
        user_agent = request.headers.get('user-agent')
        if not ip or not user_agent:
            return None
        return md5(f'{ip}{VERSION_NUMBERS.sub("", user_agent)}'.encode()).hexdigest()
