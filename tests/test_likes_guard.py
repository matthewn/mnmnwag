import re
from unittest.mock import MagicMock, patch

from django.http import HttpResponse

from mnmnwag.middleware import (
    LIKES_RATE_LIMIT,
    LikesGuardMiddleware,
    SecretBallotClientIpUseragentMiddleware,
)
from mnmnwag.models import BlogPageMixin


def make_middleware(response=None):
    """
    Return a LikesGuardMiddleware instance whose downstream always returns `response`.
    """
    if response is None:
        response = HttpResponse('OK')
    return LikesGuardMiddleware(get_response=lambda r: response)


def make_request(path, has_viewed_blog=None, ip='1.2.3.4', forwarded=None):
    """
    Build a mock request for `path`.

    If `has_viewed_blog` is given it is written into the mock session dict; omitting
    it leaves the session empty (simulating a visitor who has never viewed a blog page).

    `ip` becomes REMOTE_ADDR and `forwarded` the X-Forwarded-For header, which is
    where the visitor's real address lives in production: gunicorn listens on a
    unix socket, so REMOTE_ADDR arrives empty and Caddy passes the address along.
    """
    request = MagicMock()
    request.path = path
    request.META = {'REMOTE_ADDR': ip}
    request.headers = {'x-forwarded-for': forwarded} if forwarded else {}
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


def test_rate_limit_cache_key_prefers_forwarded_ip():
    """
    The forwarded address wins over REMOTE_ADDR, so the counter follows the
    visitor rather than the proxy.

    The two disagree on purpose. In production REMOTE_ADDR is empty for every
    request, so keying on it gave the whole site one shared counter of
    LIKES_RATE_LIMIT likes per hour.
    """
    middleware = make_middleware()
    request = make_request('/likes/submit/', has_viewed_blog=True, ip='', forwarded='203.0.113.7')
    with patch('mnmnwag.middleware.cache') as mock_cache:
        mock_cache.incr.return_value = 1
        middleware(request)
    mock_cache.add.assert_called_once_with('likes_rl:203.0.113.7', 0, 3600)


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


# ---------------------------------------------------------------------------
# SecretBallotClientIpUseragentMiddleware
# ---------------------------------------------------------------------------

CHROME = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/141.0.0.0 Safari/537.36'
CHROME_UPDATED = CHROME.replace('141.0.0.0', '142.0.7444.59')
FIREFOX = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0'


def make_voter(forwarded='203.0.113.7', user_agent=CHROME, username=None):
    """
    Build a mock request for a voter, shaped like production: REMOTE_ADDR is
    empty and the address arrives in a header. `username` makes them logged in.
    """
    request = MagicMock()
    request.META = {'REMOTE_ADDR': ''}
    request.headers = {}
    if forwarded:
        request.headers['x-forwarded-for'] = forwarded
    if user_agent:
        request.headers['user-agent'] = user_agent
    request.user.is_authenticated = username is not None
    request.user.username = username
    return request


def token_for(**kwargs):
    """
    The ballot token the middleware would hand the given voter.
    """
    middleware = SecretBallotClientIpUseragentMiddleware(get_response=lambda r: HttpResponse('OK'))
    return middleware.generate_token(make_voter(**kwargs))


def test_ballot_token_survives_a_browser_update():
    """
    The same reader keeps their ballot when their browser updates.

    Version numbers are stripped for exactly this: without it every Chrome
    release would mint a new voter, letting everyone vote again every few weeks.
    """
    assert token_for(user_agent=CHROME) == token_for(user_agent=CHROME_UPDATED)


def test_different_browsers_get_different_ballot_tokens():
    """
    Stripping versions must not go so far that two browsers become one voter.
    """
    assert token_for(user_agent=CHROME) != token_for(user_agent=FIREFOX)


def test_different_forwarded_ips_get_different_ballot_tokens():
    """
    Two readers on one browser are two voters, though REMOTE_ADDR is identical
    (and empty) for both.

    This is the bug the class exists to fix: keying on REMOTE_ADDR made the
    user agent the whole identity, so strangers voted on each other's behalf.
    """
    assert token_for(forwarded='203.0.113.7') != token_for(forwarded='198.51.100.4')


def test_ballot_token_uses_username_when_logged_in():
    """
    A logged-in voter is identified by name, as the parent class intends.
    """
    assert token_for(username='groovy') == 'groovy'


def test_ballot_token_is_none_without_an_address():
    """
    No address means no token, rather than one bucket shared by everyone.
    """
    assert token_for(forwarded=None) is None


def test_ballot_token_is_none_without_a_user_agent():
    """
    Same for a request that sends no user agent.
    """
    assert token_for(user_agent=None) is None


def test_ballot_token_is_attached_to_the_request():
    """
    The token reaches the view the way secretballot expects to find it.

    Asserts a real digest rather than just equality with token_for(): override
    generate_token() under the wrong name and the parent's version runs
    instead, handing both sides of that comparison an identical None.
    """
    middleware = SecretBallotClientIpUseragentMiddleware(get_response=lambda r: HttpResponse('OK'))
    request = make_voter()
    middleware(request)
    assert request.secretballot_token == token_for()
    assert re.fullmatch(r'[0-9a-f]{32}', request.secretballot_token)
