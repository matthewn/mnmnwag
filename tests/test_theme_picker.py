from unittest.mock import MagicMock

from django.http import HttpResponse
from django.test import RequestFactory

from mnmnwag.middleware import ThemeClassCacheMiddleware
from mnmnwag.templatetags.get_theme_class import get_theme_class
from mnmnwag.views import theme_picker


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_middleware(response=None):
    if response is None:
        response = HttpResponse('OK')
    return ThemeClassCacheMiddleware(get_response=lambda r: response)


def make_request(cookies=None):
    request = MagicMock()
    request.COOKIES = cookies or {}
    request.META = {}
    return request


def make_context(meta=None, cookies=None):
    request = MagicMock()
    request.META = meta or {}
    request.COOKIES = cookies or {}
    return {'request': request}


# ---------------------------------------------------------------------------
# ThemeClassCacheMiddleware — HTTP_X_THEME_CLASS
# ---------------------------------------------------------------------------

def test_middleware_sets_header_from_light_cookie():
    middleware = make_middleware()
    request = make_request({'themeClass': 'theme-light'})
    middleware(request)
    assert request.META['HTTP_X_THEME_CLASS'] == 'theme-light'


def test_middleware_sets_header_from_dark_cookie():
    middleware = make_middleware()
    request = make_request({'themeClass': 'theme-dark'})
    middleware(request)
    assert request.META['HTTP_X_THEME_CLASS'] == 'theme-dark'


def test_middleware_sets_header_from_retro_cookie():
    middleware = make_middleware()
    request = make_request({'themeClass': 'theme-retro'})
    middleware(request)
    assert request.META['HTTP_X_THEME_CLASS'] == 'theme-retro'


def test_middleware_defaults_to_theme_light_when_no_cookie():
    middleware = make_middleware()
    request = make_request()
    middleware(request)
    assert request.META['HTTP_X_THEME_CLASS'] == 'theme-light'


# ---------------------------------------------------------------------------
# ThemeClassCacheMiddleware — Vary header
# ---------------------------------------------------------------------------

def test_middleware_adds_vary_x_theme_class():
    response = HttpResponse('OK')
    middleware = make_middleware(response)
    request = make_request()
    result = middleware(request)
    assert 'X-Theme-Class' in result['Vary']


def test_middleware_appends_to_existing_vary_header():
    response = HttpResponse('OK')
    response['Vary'] = 'Accept-Encoding'
    middleware = make_middleware(response)
    request = make_request()
    result = middleware(request)
    vary = result['Vary']
    assert 'Accept-Encoding' in vary
    assert 'X-Theme-Class' in vary


# ---------------------------------------------------------------------------
# get_theme_class template tag
# ---------------------------------------------------------------------------

def test_tag_reads_meta_header_in_production():
    """
    When HTTP_X_THEME_CLASS is set (i.e. ThemeClassCacheMiddleware ran),
    the tag returns that value — not the cookie.
    """
    context = make_context(meta={'HTTP_X_THEME_CLASS': 'theme-dark'})
    assert get_theme_class(context) == 'theme-dark'


def test_tag_meta_header_wins_over_conflicting_cookie():
    """
    Regression: wagtail-cache strips themeClass from request.COOKIES before
    the view runs. The tag must prefer HTTP_X_THEME_CLASS (set earlier, before
    the stripping) over the (now-empty) cookie.
    """
    context = make_context(
        meta={'HTTP_X_THEME_CLASS': 'theme-dark'},
        cookies={'themeClass': 'theme-light'},
    )
    assert get_theme_class(context) == 'theme-dark'


def test_tag_falls_back_to_cookie_when_no_meta_header():
    """
    Without ThemeClassCacheMiddleware (e.g. local dev), the tag reads the cookie.
    """
    context = make_context(cookies={'themeClass': 'theme-retro'})
    assert get_theme_class(context) == 'theme-retro'


def test_tag_defaults_to_theme_light_when_nothing_set():
    context = make_context()
    assert get_theme_class(context) == 'theme-light'


def test_tag_defaults_to_theme_light_on_missing_request():
    assert get_theme_class({}) == 'theme-light'


# ---------------------------------------------------------------------------
# theme_picker view
# ---------------------------------------------------------------------------

rf = RequestFactory()


def picker_request(theme, referer='http://testserver/blog/'):
    request = rf.get(f'/theme/{theme}', HTTP_REFERER=referer)
    return request


def test_picker_redirects_to_referer():
    response = theme_picker(picker_request('dark'), 'dark')
    assert response.status_code == 302
    assert response['Location'] == 'http://testserver/blog/'


def test_picker_sets_light_cookie():
    response = theme_picker(picker_request('light'), 'light')
    assert response.cookies['themeClass'].value == 'theme-light'


def test_picker_sets_dark_cookie():
    response = theme_picker(picker_request('dark'), 'dark')
    assert response.cookies['themeClass'].value == 'theme-dark'


def test_picker_sets_retro_cookie():
    response = theme_picker(picker_request('retro'), 'retro')
    assert response.cookies['themeClass'].value == 'theme-retro'


def test_picker_ignores_invalid_theme():
    response = theme_picker(picker_request('hacker'), 'hacker')
    assert 'themeClass' not in response.cookies


def test_picker_cookie_is_samesite_strict():
    response = theme_picker(picker_request('dark'), 'dark')
    assert response.cookies['themeClass']['samesite'] == 'strict'


def test_picker_cookie_has_future_expiry():
    import datetime
    response = theme_picker(picker_request('dark'), 'dark')
    expires_str = response.cookies['themeClass']['expires']
    # Django formats this as an HTTP date string; parse it back.
    from email.utils import parsedate_to_datetime
    expires = parsedate_to_datetime(expires_str)
    assert expires > datetime.datetime.now(tz=datetime.timezone.utc)
