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
