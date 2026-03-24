from unittest.mock import MagicMock, patch

from django.http import HttpResponse

from mnmnwag.middleware import LIKES_RATE_LIMIT, LikesGuardMiddleware
from mnmnwag.models import BlogPageMixin


def make_middleware(response=None):
    """
    Return a LikesGuardMiddleware instance whose downstream always returns `response`.
    """
    if response is None:
        response = HttpResponse('OK')
    return LikesGuardMiddleware(get_response=lambda r: response)


def make_request(path, has_viewed_blog=None, ip='1.2.3.4'):
    """
    Build a mock request for `path`.

    If `has_viewed_blog` is given it is written into the mock session dict; omitting
    it leaves the session empty (simulating a visitor who has never viewed a blog page).
    """
    request = MagicMock()
    request.path = path
    request.META = {'REMOTE_ADDR': ip}
    request.session = {}
    if has_viewed_blog is not None:
        request.session['has_viewed_blog'] = has_viewed_blog
    return request


# ---------------------------------------------------------------------------
# Non-likes paths
# ---------------------------------------------------------------------------

def test_non_likes_path_passes_through():
    """
    Requests to ordinary pages are never intercepted, even without a session flag.
    """
    middleware = make_middleware()
    request = make_request('/blog/post/')
    response = middleware(request)
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# Session guard
# ---------------------------------------------------------------------------

def test_likes_without_session_flag_returns_403():
    """
    A /likes/ request from a session with no blog-view history is rejected with 403.
    """
    middleware = make_middleware()
    request = make_request('/likes/submit/')
    response = middleware(request)
    assert response.status_code == 403


def test_likes_with_false_session_flag_returns_403():
    """
    Explicitly False is treated the same as absent — the visitor has not earned like access.
    """
    middleware = make_middleware()
    request = make_request('/likes/submit/', has_viewed_blog=False)
    response = middleware(request)
    assert response.status_code == 403


# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------

def test_likes_within_rate_limit_passes():
    """
    A session-flagged request well within the rate limit is allowed through.
    """
    middleware = make_middleware()
    request = make_request('/likes/submit/', has_viewed_blog=True)
    with patch('mnmnwag.middleware.cache') as mock_cache:
        mock_cache.incr.return_value = 1
        response = middleware(request)
    assert response.status_code == 200


def test_likes_at_rate_limit_passes():
    """
    A request that hits exactly LIKES_RATE_LIMIT is still allowed (limit is inclusive).
    """
    middleware = make_middleware()
    request = make_request('/likes/submit/', has_viewed_blog=True)
    with patch('mnmnwag.middleware.cache') as mock_cache:
        mock_cache.incr.return_value = LIKES_RATE_LIMIT
        response = middleware(request)
    assert response.status_code == 200


def test_likes_over_rate_limit_returns_429():
    """
    One request beyond LIKES_RATE_LIMIT triggers a 429 Too Many Requests response.
    """
    middleware = make_middleware()
    request = make_request('/likes/submit/', has_viewed_blog=True)
    with patch('mnmnwag.middleware.cache') as mock_cache:
        mock_cache.incr.return_value = LIKES_RATE_LIMIT + 1
        response = middleware(request)
    assert response.status_code == 429


def test_rate_limit_cache_key_uses_ip():
    """
    The cache key used for rate-limiting is derived from the request IP.

    This ensures separate IPs get separate counters and a busy shared IP cannot
    starve out others on the same network.
    """
    middleware = make_middleware()
    request = make_request('/likes/submit/', has_viewed_blog=True, ip='10.0.0.1')
    with patch('mnmnwag.middleware.cache') as mock_cache:
        mock_cache.incr.return_value = 1
        middleware(request)
    mock_cache.add.assert_called_once_with('likes_rl:10.0.0.1', 0, 3600)


# ---------------------------------------------------------------------------
# BlogPageMixin
# ---------------------------------------------------------------------------

class _Parent:
    """
    Minimal stand-in for a Wagtail Page base class with a serve() method.
    """

    def serve(self, request, *args, **kwargs):
        return HttpResponse('OK')


class _TestPage(BlogPageMixin, _Parent):
    """
    Concrete page type that combines BlogPageMixin with the stub parent.
    """
    pass


def test_blog_page_mixin_sets_session_flag():
    """
    Serving a blog page sets has_viewed_blog=True in the session.

    This is what allows subsequent /likes/ requests to pass the session guard.
    """
    page = _TestPage()
    request = MagicMock()
    request.session = {}
    page.serve(request)
    assert request.session.get('has_viewed_blog') is True


def test_blog_page_mixin_returns_parent_response():
    """
    BlogPageMixin.serve() returns whatever the parent's serve() returns.
    """
    page = _TestPage()
    request = MagicMock()
    request.session = {}
    response = page.serve(request)
    assert response.status_code == 200


def test_blog_page_mixin_passes_args_to_parent():
    """
    Extra positional and keyword arguments are forwarded to super().serve() unchanged.
    """
    received = {}

    class _TrackingParent:
        def serve(self, request, *args, **kwargs):
            received['args'] = args
            received['kwargs'] = kwargs
            return HttpResponse('OK')

    class _TrackingPage(BlogPageMixin, _TrackingParent):
        pass

    page = _TrackingPage()
    request = MagicMock()
    request.session = {}
    page.serve(request, 'a', key='b')
    assert received['args'] == ('a',)
    assert received['kwargs'] == {'key': 'b'}
