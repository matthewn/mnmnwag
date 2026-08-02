"""
Tests for lightbox.js, driven through a real browser.

The server side is covered by test_slide_lightbox.py; this file starts where
that one stops, at the markup it hands the browser. Everything here runs
against a live Django and a real Chromium, because the lightbox is mostly
gestures and layout -- a scroll-snap track, pointer capture, scrollend -- and a
DOM stub with no layout would only be able to test the stubs.

A note on what is being served. The page asks for its js through {% static %}
and {% compress %}, both of which normally answer out of the collected static/
directory -- which is whatever was last written there by collectstatic, not
mnmnwag/static/js/lightbox.js. Left alone, this file would test a stale copy
and pass while the real one was broken, so the assets fixture below turns both
off and lets the staticfiles finders serve the source.
"""
import json
import os
import re

# Playwright's sync API drives its event loop on a greenlet in this thread, and
# asyncio's running-loop flag is per thread rather than per greenlet -- so Django
# sees an event loop and refuses to open or close a connection. Nothing here is
# actually async; the guard is reading the wrong signal. Set at import, which is
# collection time, so it is in place before the first database access.
os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'

import pytest
from django.db import connections
from playwright.sync_api import expect
from urllib.parse import urlparse
from wagtail.images import get_image_model
from wagtail.images.tests.utils import get_test_image_file
from wagtail.models import Site

from mnmnwag.models import ComplexPage, GalleryPage

# Every test here starts a browser and a live server, which costs a couple of
# minutes. pyproject.toml deselects the mark by default, so a plain `pytest`
# skips the lot; `pytest -m browser` is what runs them.
pytestmark = pytest.mark.browser

BLOCK_ID = 'abcdefg1-2345-6789-abcd-ef0123456789'
SLIDES = 4
VIEWPORT = {'width': 1000, 'height': 800}
PHONE = {'width': 400, 'height': 800}

# Long enough that the track has plainly stopped moving and Unpoly has plainly
# had its chance, so "nothing happened" means nothing was going to happen.
QUIET_MS = 600


# ---------------------------------------------------------------------------
# the harness
# ---------------------------------------------------------------------------

@pytest.fixture(scope='session')
def browser_type_launch_args(browser_type_launch_args):
    """
    Both zoom views 404 unless the host looks like the real site, and the live
    server answers on localhost. Resolve the real hostname to it in the browser
    rather than reaching for the view's own idea of who it serves.
    """
    return {
        **browser_type_launch_args,
        'args': [
            *browser_type_launch_args.get('args', []),
            '--host-resolver-rules=MAP mahnamahna.test 127.0.0.1',
        ],
    }


@pytest.fixture(scope='session')
def base_url(live_server):
    """
    Overrides pytest-base-url's fixture, so page.goto() takes a path.
    """
    return f'http://mahnamahna.test:{urlparse(live_server.url).port}'


@pytest.fixture(scope='session', autouse=True)
def _restorable_baseline(django_db_setup, django_db_blocker):
    """
    Every test here needs live_server, which pytest-django answers by making the
    test transactional -- and a transactional test truncates every table on the
    way out, taking Wagtail's root page, default Site and root Collection with
    it. Django restores that baseline afterwards from a snapshot it stashes on
    the connection during test-database setup, but the connection object this
    thread holds is not the one carrying the snapshot: Playwright runs us on a
    greenlet, greenlets get their own contextvars, and the connection handler
    keeps its connections in one. The restore then quietly does not happen and
    every test after the first one builds its pages on an empty database.

    So take the snapshot here, where it can be read, and hang it on the
    connection *class* -- where every wrapper in every context and thread will
    find it, and Django's own machinery does the rest.
    """
    with django_db_blocker.unblock():
        contents = connections['default'].creation.serialize_db_to_string()
    type(connections['default'])._test_serialized_contents = contents
    yield
    del type(connections['default'])._test_serialized_contents


@pytest.fixture(autouse=True)
def source_assets(settings):
    """
    Serve mnmnwag/static/js/lightbox.js rather than the collected copy: with
    compression off the template emits one script tag per file, and with the
    plain storage backend {% static %} stops asking a manifest -- built by the
    last collectstatic -- what those files are called. Both then fall to the
    staticfiles finders, which look in the app first.
    """
    settings.COMPRESS_ENABLED = False
    settings.STORAGES = {
        **settings.STORAGES,
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    }


@pytest.fixture
def gallery(transactional_db, django_db_serialized_rollback):
    """
    A gallery of four slides, hung under a page that can lend it a
    page_message -- which a GalleryPage takes from its parent.
    """
    Site.clear_site_root_paths_cache()
    images = [
        get_image_model().objects.create(
            title=f'slide {i}',
            description='a description',
            file=get_test_image_file(size=(900, 600)),
        )
        for i in range(SLIDES)
    ]
    parent = ComplexPage(title='a post', slug='a-post', page_message='<p>hello</p>')
    Site.objects.get(is_default_site=True).root_page.add_child(instance=parent)
    page = GalleryPage(
        title='a gallery',
        slug='a-gallery',
        body=json.dumps([{
            'type': 'slides',
            'id': BLOCK_ID,
            'value': {'slides': [
                {'image': image.id, 'caption': f'<p>caption {i}</p>', 'alt_text': ''}
                for i, image in enumerate(images)
            ]},
        }]),
    )
    parent.add_child(instance=page)
    yield page
    Site.clear_site_root_paths_cache()


@pytest.fixture
def open_slide(gallery, page, base_url):
    """
    Open a slide by its own URL, which puts the lightbox on the root layer.
    """
    def open_(pos=1):
        page.set_viewport_size(VIEWPORT)
        page.goto(slide_path(gallery, pos))
        page.wait_for_selector('[up-lightbox]')
        return page
    return open_


@pytest.fixture
def open_overlay(gallery, page, base_url):
    """
    Open a slide the way a visitor does, by clicking a thumbnail on the post,
    which puts the lightbox in an Unpoly overlay instead.
    """
    def open_(pos=0):
        page.set_viewport_size(VIEWPORT)
        page.goto(gallery.url)
        page.locator('.slide a').nth(pos).click()
        page.wait_for_selector('[up-lightbox]')
        return page
    return open_


@pytest.fixture
def touch_page(gallery, browser, base_url):
    """
    A phone-shaped context that reports a touchscreen, so the lightbox binds and
    trusts its touch handlers.
    """
    context = browser.new_context(base_url=base_url, has_touch=True, viewport=PHONE)
    page = context.new_page()

    def open_(pos=1):
        page.goto(slide_path(gallery, pos))
        page.wait_for_selector('[up-lightbox]')
        return page

    yield open_
    context.close()


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def slide_path(gallery, pos):
    return f'/slide/{gallery.id}/{BLOCK_ID[:7]}/{pos}'


def expect_slide(page, gallery, pos):
    """
    Where the lightbox says it is, by both of the things it keeps in step: the
    address it rewrites and the counter it draws.
    """
    expect(page).to_have_url(re.compile(rf'{slide_path(gallery, pos)}$'))
    expect(page.locator('[up-lightbox-counter]')).to_have_text(f'{pos + 1} / {SLIDES}')


def track_state(page):
    return page.evaluate("""() => {
        const track = document.querySelector('[up-lightbox-track]');
        const current = document.querySelector('.lightbox-panel.is-current');
        return {left: track.scrollLeft, width: track.clientWidth, panel: current.offsetLeft};
    }""")


def mouse_drag(page, dx=0, dy=0, steps=10):
    """
    Press on the photo and drag, a step per frame, the way the desktop swipe is
    meant to be used.
    """
    box = page.locator('.lightbox-panel.is-current img').bounding_box()
    x, y = box['x'] + box['width'] / 2, box['y'] + box['height'] / 2
    page.mouse.move(x, y)
    page.mouse.down()
    for step in range(1, steps + 1):
        page.mouse.move(x + dx * step / steps, y + dy * step / steps)
        page.wait_for_timeout(16)
    page.mouse.up()


# A touch drag, dispatched rather than driven: Chromium's synthetic touch does
# not carry the momentum and snapping the real gesture rides on, and it is the
# handlers' own arithmetic -- how far, how vertical, did the track stay put --
# that is under test here.
TOUCH_DRAG = """
    ([selector, dy]) => {
        const el = document.querySelector(selector);
        const at = (y) => new Touch({identifier: 1, target: el, clientX: 200, clientY: y});
        const fire = (type, y) => el.dispatchEvent(new TouchEvent(type, {
            bubbles: true,
            cancelable: true,
            touches: type === 'touchend' ? [] : [at(y)],
            changedTouches: [at(y)],
        }));
        fire('touchstart', 300);
        for (let step = 20; step <= Math.abs(dy); step += 20) {
            fire('touchmove', 300 + Math.sign(dy) * step);
        }
        fire('touchend', 300 + dy);
    }
"""


def touch_drag(page, dy, selector='.lightbox-panel.is-current img'):
    page.evaluate(TOUCH_DRAG, [selector, dy])


# ---------------------------------------------------------------------------
# what the compiler sets up
# ---------------------------------------------------------------------------

def test_the_neighbors_are_handed_their_sources(open_slide):
    """
    They ship inert so a nojs visitor is not billed for two extra photos; with
    js they have to be loadable before a swipe reaches them.
    """
    page = open_slide()
    loadable = page.evaluate(
        "[...document.querySelectorAll('.lightbox-panel img')]"
        ".map((img) => Boolean(img.getAttribute('src') && img.getAttribute('srcset')))"
    )
    assert loadable == [True, True, True]


def test_the_track_starts_centered_on_the_current_slide(open_slide):
    """
    Anywhere else and the track is nearest a neighbor, which settled() would
    read as a swipe and follow.
    """
    state = track_state(open_slide())
    assert state['left'] == state['panel']


# ---------------------------------------------------------------------------
# the keys
# ---------------------------------------------------------------------------

def test_right_arrow_moves_on(open_slide, gallery):
    page = open_slide(1)
    page.keyboard.press('ArrowRight')
    expect_slide(page, gallery, 2)


def test_left_arrow_goes_back(open_slide, gallery):
    page = open_slide(1)
    page.keyboard.press('ArrowLeft')
    expect_slide(page, gallery, 0)


def test_the_arrows_stop_at_the_first_slide(open_slide, gallery):
    """
    There is no previous link to follow, and nothing should be invented: the
    press is left unhandled and the slide stays put.
    """
    page = open_slide(0)
    page.keyboard.press('ArrowLeft')
    page.wait_for_timeout(QUIET_MS)
    expect_slide(page, gallery, 0)


def test_the_arrows_stop_at_the_last_slide(open_slide, gallery):
    page = open_slide(SLIDES - 1)
    page.keyboard.press('ArrowRight')
    page.wait_for_timeout(QUIET_MS)
    expect_slide(page, gallery, SLIDES - 1)


def test_end_reaches_past_the_three_up_window(open_slide, gallery):
    """
    The last slide is not in the DOM, so this cannot be a scroll: it is the jump
    link, retargeted through the URL template.
    """
    page = open_slide(0)
    page.keyboard.press('End')
    expect_slide(page, gallery, SLIDES - 1)


def test_home_reaches_back_past_it(open_slide, gallery):
    page = open_slide(SLIDES - 1)
    page.keyboard.press('Home')
    expect_slide(page, gallery, 0)


def test_held_arrows_make_one_jump_rather_than_a_walk(open_slide, gallery):
    """
    Twelve taps means one navigation twelve slides over. Three quick presses
    from the first slide should therefore ask for the fourth outright, rather
    than fetching its way there a slide at a time.
    """
    page = open_slide(0)
    asked_for = []
    page.on('request', lambda request: (
        asked_for.append(request.url) if '/slide/' in request.url else None
    ))

    for _ in range(3):
        page.keyboard.press('ArrowRight')

    expect_slide(page, gallery, 3)
    assert asked_for[0].endswith(slide_path(gallery, 3))


def test_the_counter_names_where_a_press_is_headed(open_slide, gallery):
    """
    A keypress knows its destination before the fetch that serves it lands, and
    says so. With the fetch refused outright, what is left on screen is that
    promise -- the counter naming a slide the browser never received.
    """
    page = open_slide(0)
    page.route('**/slide/**', lambda route: route.abort())

    page.keyboard.press('ArrowRight')
    page.keyboard.press('ArrowRight')

    expect(page.locator('[up-lightbox-counter]')).to_have_text(f'3 / {SLIDES}')
    expect(page).to_have_url(re.compile(rf'{slide_path(gallery, 0)}$'))


def test_a_press_after_several_slides_still_moves_only_one(open_slide, gallery):
    """
    Every slide change replaces the lightbox and runs the compiler again. If a
    replaced fragment's listeners outlived it, the surviving copies would each
    take their own step from the same banked position, and one press would move
    as many slides as there have been lightboxes.
    """
    page = open_slide(0)
    for pos in (1, 2, 3):
        page.keyboard.press('ArrowRight')
        expect_slide(page, gallery, pos)

    page.keyboard.press('ArrowLeft')
    expect_slide(page, gallery, 2)


# ---------------------------------------------------------------------------
# the ways out
# ---------------------------------------------------------------------------

def test_clicking_beside_the_photo_closes(open_slide, gallery):
    """
    A directly visited slide has no overlay to dismiss, so leaving is a load of
    the post itself.
    """
    page = open_slide()
    box = page.locator('.lightbox-panel.is-current img').bounding_box()
    page.mouse.click(box['x'] + box['width'] / 2, box['y'] + box['height'] + 20)
    expect(page).to_have_url(re.compile(f'{gallery.url}$'))


def test_clicking_the_photo_keeps_it_open(open_slide, gallery):
    page = open_slide()
    page.locator('.lightbox-panel.is-current img').click()
    page.wait_for_timeout(QUIET_MS)
    expect_slide(page, gallery, 1)


def test_clicking_a_caption_keeps_it_open(open_slide, gallery):
    """
    A caption is there to be read, and reading it means clicking into it to
    select and scroll.
    """
    page = open_slide()
    page.locator('.lightbox-panel.is-current figcaption').click()
    page.wait_for_timeout(QUIET_MS)
    expect_slide(page, gallery, 1)


def test_the_close_button_goes_back_to_the_post(open_slide, gallery):
    page = open_slide()
    page.locator('.lightbox-close').click()
    expect(page).to_have_url(re.compile(f'{gallery.url}$'))


def test_escape_closes_a_directly_visited_slide(open_slide, gallery):
    """
    An overlay closes itself on Escape; the root layer has to be sent somewhere.
    """
    page = open_slide()
    page.keyboard.press('Escape')
    expect(page).to_have_url(re.compile(f'{gallery.url}$'))


def test_escape_dismisses_the_overlay_and_gives_the_post_back(open_overlay, gallery):
    page = open_overlay()
    page.keyboard.press('Escape')
    expect(page).to_have_url(re.compile(f'{gallery.url}$'))
    expect(page.locator('[up-lightbox]')).to_have_count(0)


def test_the_overlay_box_is_named(open_overlay):
    """
    Unpoly marks its box role="dialog" and leaves it unnamed, which is a dialog
    a screen reader can only announce as "dialog".
    """
    page = open_overlay()
    expect(page.locator('up-modal-box')).to_have_attribute('aria-label', 'Lightbox')


def test_walking_the_slides_leaves_no_history_entries(open_overlay, gallery):
    """
    Unpoly would push an entry per slide, turning Back into a walk through
    everything just looked at. The lightbox commandeers the entry it was opened
    on and rewrites it instead, so Back leaves the post outright.
    """
    page = open_overlay()
    entries = page.evaluate('history.length')

    page.keyboard.press('ArrowRight')
    expect_slide(page, gallery, 1)
    page.keyboard.press('ArrowRight')
    expect_slide(page, gallery, 2)

    assert page.evaluate('history.length') == entries


# ---------------------------------------------------------------------------
# the slideshow
#
# Its waits are seconds long, so these run against Playwright's clock rather
# than the wall: install() freezes time, fast_forward() spends it.
# ---------------------------------------------------------------------------

def test_the_slideshow_advances_a_slide_at_a_time(page, open_slide, gallery):
    page.clock.install()
    open_slide(0)

    page.locator('[up-lightbox-slideshow]').click()
    expect(page.locator('[up-lightbox-slideshow]')).to_have_attribute('aria-label',
                                                                     'Stop slideshow')

    page.clock.fast_forward(7000)
    expect_slide(page, gallery, 1)
    page.clock.fast_forward(7000)
    expect_slide(page, gallery, 2)


def test_the_slideshow_stops_when_it_runs_out_of_slides(page, open_slide, gallery):
    """
    Each slide schedules only its own advance, so the show simply stops when it
    reaches one with nowhere further to go -- and says so, rather than leaving a
    button that claims to be playing.
    """
    page.clock.install()
    open_slide(SLIDES - 2)

    page.locator('[up-lightbox-slideshow]').click()
    page.clock.fast_forward(7000)

    expect_slide(page, gallery, SLIDES - 1)
    expect(page.locator('[up-lightbox-slideshow]')).to_have_attribute('aria-label',
                                                                     'Start slideshow')
    expect(page.locator('[up-lightbox-slideshow]')).not_to_have_class(re.compile('is-on'))


def test_a_keypress_takes_the_slideshow_back(page, open_slide, gallery):
    page.clock.install()
    open_slide(0)

    page.locator('[up-lightbox-slideshow]').click()
    page.keyboard.press('ArrowRight')

    expect_slide(page, gallery, 1)
    expect(page.locator('[up-lightbox-slideshow]')).to_have_attribute('aria-label',
                                                                     'Start slideshow')


# ---------------------------------------------------------------------------
# the desktop drag
# ---------------------------------------------------------------------------

def test_the_photo_does_not_start_a_drag_of_its_own(open_slide):
    """
    Without this the browser tears off a ghost image the moment the grab starts.
    """
    page = open_slide()
    assert page.evaluate("""() => {
        const img = document.querySelector('.lightbox-panel.is-current img');
        const event = new DragEvent('dragstart', {bubbles: true, cancelable: true});
        img.dispatchEvent(event);
        return event.defaultPrevented;
    }""")


def test_dragging_the_photo_sideways_changes_slide(open_slide, gallery):
    """
    The drag pans the track, and it is the track settling that navigates -- the
    same route a swipe takes.
    """
    page = open_slide(1)
    mouse_drag(page, dx=-200)
    expect_slide(page, gallery, 2)


def test_a_short_sideways_drag_goes_back_where_it_was(open_slide, gallery):
    page = open_slide(1)
    mouse_drag(page, dx=-40)
    page.wait_for_timeout(QUIET_MS)
    expect_slide(page, gallery, 1)
    state = track_state(page)
    assert state['left'] == state['panel']


def test_a_drag_release_is_not_a_click_on_the_backdrop(open_slide, gallery):
    """
    Pointer capture retargets the click that ends a drag to the track, where a
    plain click means "close this".
    """
    page = open_slide(1)
    mouse_drag(page, dx=-200)
    expect(page.locator('[up-lightbox]')).to_have_count(1)


def test_dragging_the_photo_down_dismisses_it(open_slide, gallery):
    page = open_slide()
    mouse_drag(page, dy=200)
    expect(page).to_have_url(re.compile(f'{gallery.url}$'))


def test_a_short_downward_drag_springs_back(open_slide, gallery):
    """
    Short of the threshold the photo returns, having shown what it was about to
    do.
    """
    page = open_slide()
    mouse_drag(page, dy=40)
    page.wait_for_timeout(QUIET_MS)
    expect_slide(page, gallery, 1)
    assert page.evaluate(
        "document.querySelector('.lightbox-panel.is-current').style.transform"
    ) == ''


# ---------------------------------------------------------------------------
# the touch gestures
# ---------------------------------------------------------------------------

def test_a_swipe_up_or_down_closes(touch_page, gallery):
    page = touch_page()
    touch_drag(page, dy=200)
    expect(page).to_have_url(re.compile(f'{gallery.url}$'))


def test_a_swipe_that_starts_on_a_caption_is_left_alone(touch_page, gallery):
    """
    A caption long enough to scroll keeps its own vertical gestures.
    """
    page = touch_page()
    touch_drag(page, dy=200, selector='.lightbox-panel.is-current figcaption')
    page.wait_for_timeout(QUIET_MS)
    expect_slide(page, gallery, 1)
    assert page.evaluate(
        "document.querySelector('.lightbox-panel.is-current').style.transform"
    ) == ''


# ---------------------------------------------------------------------------
# the viewport moving under it
# ---------------------------------------------------------------------------

def test_a_resize_recenters_the_track(open_slide, gallery):
    """
    A resize moves every panel; left where it was, the track sits nearest a
    neighbor and the next settle reads that as a swipe.
    """
    page = open_slide()
    page.set_viewport_size({'width': 700, 'height': 600})

    page.wait_for_timeout(QUIET_MS)
    state = track_state(page)
    assert state['width'] == 700
    assert state['left'] == state['panel']
    expect_slide(page, gallery, 1)
