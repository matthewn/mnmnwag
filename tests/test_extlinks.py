from unittest.mock import MagicMock, patch

from django.http import HttpResponse

from extlinks.middleware import RewriteExternalLinksMiddleware


def html_response(html):
    return HttpResponse(html, content_type="text/html; charset=utf-8")


# ---------------------------------------------------------------------------
# _rewrite_links
# ---------------------------------------------------------------------------

def test_external_link_gets_target_blank():
    response = html_response('<a href="https://example.com">link</a>')
    RewriteExternalLinksMiddleware._rewrite_links(response)
    assert b'target="_blank" href="https://example.com"' in response.content


def test_internal_link_unchanged():
    html = '<a href="/internal/">link</a>'
    response = html_response(html)
    RewriteExternalLinksMiddleware._rewrite_links(response)
    assert response.content == html.encode()


def test_already_targeted_link_unchanged():
    html = '<a href="https://example.com" target="_self">link</a>'
    response = html_response(html)
    RewriteExternalLinksMiddleware._rewrite_links(response)
    assert b'target="_blank"' not in response.content


def test_ignored_domain_unchanged():
    html = '<a href="https://www.mahnamahna.net/page">link</a>'
    response = html_response(html)
    RewriteExternalLinksMiddleware._rewrite_links(response)
    assert b'target="_blank"' not in response.content


def test_external_link_with_prior_attributes():
    response = html_response('<a class="foo" href="https://example.com">link</a>')
    RewriteExternalLinksMiddleware._rewrite_links(response)
    assert b'target="_blank" href=' in response.content


def test_multiple_external_links_all_rewritten():
    response = html_response(
        '<a href="https://one.com">1</a> <a href="https://two.com">2</a>'
    )
    RewriteExternalLinksMiddleware._rewrite_links(response)
    assert response.content.count(b'target="_blank"') == 2


def test_mailto_link_unchanged():
    html = '<a href="mailto:foo@example.com">email</a>'
    response = html_response(html)
    RewriteExternalLinksMiddleware._rewrite_links(response)
    assert b'target="_blank"' not in response.content


# ---------------------------------------------------------------------------
# process_template_response
# ---------------------------------------------------------------------------

def make_middleware():
    return RewriteExternalLinksMiddleware(get_response=lambda r: r)


def test_streaming_response_skipped():
    middleware = make_middleware()
    response = MagicMock()
    response.streaming = True
    middleware.process_template_response(MagicMock(), response)
    response.add_post_render_callback.assert_not_called()


def test_empty_whitelist_skipped():
    middleware = make_middleware()
    response = MagicMock()
    response.streaming = False
    with patch("extlinks.middleware.templates_whitelist", []):
        middleware.process_template_response(MagicMock(), response)
    response.add_post_render_callback.assert_not_called()


def test_template_not_in_whitelist_skipped():
    middleware = make_middleware()
    response = MagicMock()
    response.streaming = False
    response.template_name = "some_other_app/page.html"
    middleware.process_template_response(MagicMock(), response)
    response.add_post_render_callback.assert_not_called()


def test_template_in_whitelist_registers_callback():
    middleware = make_middleware()
    response = MagicMock()
    response.streaming = False
    response.template_name = "mnmnwag/base.html"
    middleware.process_template_response(MagicMock(), response)
    response.add_post_render_callback.assert_called_once_with(
        RewriteExternalLinksMiddleware._rewrite_links
    )
