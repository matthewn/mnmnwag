from django.test import Client

from mnmnwag.models import ModernPost


def _a_post():
    """
    Return the most recent live, public post.
    """
    return ModernPost.objects.live().public().order_by('-first_published_at').first()


def test_canonical_date_url_serves(read_only_db):
    """
    A post's canonical date-prefixed URL serves directly, with no redirect.
    """
    post = _a_post()
    canonical = post.get_url_parts()[2]  # the relative page_path
    response = Client().get(canonical)
    assert response.status_code == 200


def test_legacy_slug_url_redirects(read_only_db):
    """
    A post's legacy slug-only URL 301s to its canonical date-prefixed URL.
    """
    post = _a_post()
    canonical = post.get_url_parts()[2]
    legacy = f'/blog/{post.slug}/'
    response = Client().get(legacy)
    assert response.status_code == 301
    assert response['Location'] == canonical


def test_canonical_date_url_runs_serve_hooks(read_only_db):
    """
    The canonical date-prefixed URL runs Wagtail's serve hooks against the post
    itself, as wagtail.views.serve does. The on_serve_page hooks enforce view
    restrictions (e.g. "private, accessible with a shared password"); skipping
    them would serve a protected post to anyone.
    """
    from django.http import HttpResponse
    from wagtail import hooks

    post = _a_post()
    canonical = post.get_url_parts()[2]
    seen = {'before': [], 'on': []}

    def before(page, request, serve_args, serve_kwargs):
        seen['before'].append(page.pk)

    def on(callback):
        def inner(page, request, serve_args, serve_kwargs):
            seen['on'].append(page.pk)
            if page.pk == post.pk:
                return HttpResponse('blocked', status=401)
            return callback(page, request, serve_args, serve_kwargs)
        return inner

    with hooks.register_temporarily('before_serve_page', before), \
            hooks.register_temporarily('on_serve_page', on):
        response = Client().get(canonical)
    assert post.pk in seen['before']
    assert post.pk in seen['on']
    assert response.status_code == 401
