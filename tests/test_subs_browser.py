"""
Tests for the subscribe form's Unpoly behavior, driven through a real browser.

The server side is covered by test_subs_antibot.py; this file exists for the
one thing that file cannot see. The form swaps itself into #content, and Unpoly
routes a *failed* response (our 429) to the fail target rather than the target,
so a rate-limited visitor takes a different path through Unpoly than a visitor
who merely mistyped their address. Nothing about that is visible from a status
code, which is all the server-side tests can check.
"""
import os

# See the note in test_lightbox_js.py: Playwright's greenlet makes Django think
# it is in async context and refuse to touch the database. Set at collection
# time, before the first database access.
os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'

import pytest
from playwright.sync_api import expect
from unittest.mock import patch
from urllib.parse import urlparse
from wagtail.models import Site

pytestmark = [pytest.mark.browser, pytest.mark.usefixtures('restorable_baseline')]

EMAIL = 'reader@example.org'


@pytest.fixture(scope='session')
def base_url(live_server):
    """
    Overrides pytest-base-url's fixture, so page.goto() takes a path.

    Module-local on purpose: pytest-base-url autouses a session fixture that
    requests base_url for every test, so an override in conftest.py would pull
    live_server -- and a test database -- into the whole suite.
    """
    return f'http://mahnamahna.test:{urlparse(live_server.url).port}'


@pytest.fixture(autouse=True)
def source_assets(settings):
    """
    Serve the static files from the app rather than the collected copy, so the
    page gets a real unpoly.min.js instead of a 404 from a stale manifest.
    """
    settings.COMPRESS_ENABLED = False
    settings.STORAGES = {
        **settings.STORAGES,
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    }


@pytest.fixture
def form_page(page, base_url, transactional_db, django_db_serialized_rollback):
    """
    The subscribe form, with both the header and #content stamped in JS.

    The stamps are how these tests tell the swaps apart: a full page load or a
    body-level swap wipes both, an in-place swap of #content wipes only the
    one inside it.
    """
    Site.clear_site_root_paths_cache()
    page.goto('/sub/create')
    page.wait_for_selector('form.subs')
    page.evaluate("document.getElementById('header').dataset.stamp = 'first'")
    page.evaluate("document.getElementById('content').dataset.stamp = 'first'")
    yield page
    Site.clear_site_root_paths_cache()


def submit(page, email=EMAIL):
    """
    Fill the form and submit it, returning the response to the POST.

    Waits out the cross-fade: mid-transition the outgoing #content is still in
    the DOM alongside the incoming one, and every locator here would match two
    elements.
    """
    page.fill('input[name=email]', email)
    with page.expect_response(lambda r: r.request.method == 'POST') as info:
        page.get_by_role('button', name='subscribe').click()
    page.wait_for_selector('.up-destroying', state='detached')
    return info.value


def expect_swapped_in_place(page):
    """
    Assert the response replaced #content and left the rest of the page alone.
    """
    expect(page.locator('#header')).to_have_attribute('data-stamp', 'first')
    expect(page.locator('#content')).not_to_have_attribute('data-stamp', 'first')


def test_rate_limited_response_renders_in_place(form_page):
    """
    A 429 is swapped into #content like any other response.

    Without up-fail-target on the form, Unpoly sends a failed response to its
    own fail target instead -- which is not #content -- and the visitor gets a
    whole-page swap where every other outcome on this form is an in-place one.
    """
    with patch('subs.views.SUB_RATE_LIMIT_IP', 0):
        response = submit(form_page)
        assert response.status == 429
        expect(form_page.locator('#content')).to_contain_text('Too many subscription attempts')
    expect_swapped_in_place(form_page)


def test_validation_error_renders_in_place(form_page):
    """
    The 200 path, as a control: the same swap, so the two can be compared.

    'a@b' is a valid email address to the browser and an invalid one to Django,
    which is what gets us past HTML5 validation to the server-side error.
    """
    with patch('subs.forms.MIN_FORM_AGE', 0):
        response = submit(form_page, 'a@b')
        assert response.status == 200
        expect(form_page.locator('#content')).to_contain_text('Please enter a valid email address.')
    expect_swapped_in_place(form_page)
