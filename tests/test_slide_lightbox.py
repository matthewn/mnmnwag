"""
Tests for the lightbox: the zoom_slide and zoom_image views (mnmnwag/views.py)
and the template they share (mnmnwag/lightbox.html).

For a slide, the lightbox puts three in the DOM at once -- prev, current, next --
so a swipe can be an ordinary scroll over a snap track. Two things follow from
that, and both are what most of these tests are about: the window has to shrink
correctly at the ends of a block, and each panel has to carry a srcset, because
three full-size originals per slide is a lot to hand a phone.

An ImageBlock zoom is the degenerate case of the same thing -- a window of one,
with no neighbors to reach and so no counter, slideshow or arrows. Those tests
are at the foot of the file.
"""
import datetime as dt
import json
import re

import pytest
from django.test import Client
from wagtail.images import get_image_model
from wagtail.images.tests.utils import get_test_image_file
from wagtail.models import Site

from mnmnwag.models import BlogIndex, ComplexPage, GalleryPage, ModernPost
from mnmnwag.views import SLIDE_LARGE_WIDTH, SLIDE_SMALL_WIDTH, _slide_panel

BLOCK_ID = 'abcdefg1-2345-6789-abcd-ef0123456789'


@pytest.fixture(autouse=True)
def clear_site_root_paths():
    """
    Building pages here fills Wagtail's site-root-path cache from the test
    database. That cache is process-wide, so leaving it populated makes the
    read_only_db tests -- which run against the real database -- resolve their
    page URLs against roots that do not exist there.
    """
    Site.clear_site_root_paths_cache()
    yield
    Site.clear_site_root_paths_cache()


def make_image(**kwargs):
    kwargs.setdefault('title', 'test image')
    kwargs.setdefault('description', 'a description')
    kwargs.setdefault('file', get_test_image_file())
    return get_image_model().objects.create(**kwargs)


@pytest.fixture
def wide_image(db):
    """
    An image comfortably wider than the small rung, so a srcset is worthwhile.
    """
    return make_image(file=get_test_image_file(size=(3000, 2000)))


@pytest.fixture
def narrow_image(db):
    """
    An image below the small rung, which Wagtail would refuse to upscale.
    """
    return make_image(file=get_test_image_file(size=(800, 600)))


def slides_for(*images):
    """
    The shape zoom_slide sees after StreamField deserialization.
    """
    return [
        {'image': image, 'caption': '', 'alt_text': ''}
        for image in images
    ]


def panel_for(image):
    return _slide_panel(slides_for(image), 0, page_id=1, block_id='abcdefg')


# ---------------------------------------------------------------------------
# srcset: every rung that is a real saving, and never the original
# ---------------------------------------------------------------------------

def test_large_original_offers_two_candidates(wide_image):
    panel = panel_for(wide_image)
    candidates = panel['srcset'].split(', ')
    assert len(candidates) == 2
    assert candidates[0].endswith(f'{SLIDE_SMALL_WIDTH}w')
    assert candidates[1].endswith(f'{SLIDE_LARGE_WIDTH}w')


def test_original_is_never_a_candidate(wide_image):
    """
    A 3000px original tops out at the widest rung. Offering the original as well
    would hand a phone in landscape a multi-megabyte file to look at; the
    download button is what serves it whole.
    """
    panel = panel_for(wide_image)
    assert '3000w' not in panel['srcset']
    assert panel['src'].endswith('.png') and 'width-2800' in panel['src']


def test_middling_original_tops_out_at_its_own_width(db):
    """
    Below the widest rung there is nothing to cap: the top candidate is the
    original's own width, since Wagtail will not upscale past it.
    """
    image = make_image(file=get_test_image_file(size=(2000, 1500)))
    candidates = panel_for(image)['srcset'].split(', ')
    assert len(candidates) == 2
    assert candidates[1].endswith('2000w')


def test_small_original_offers_only_itself(narrow_image):
    """
    Wagtail does not upscale, so a width-1200 rendition of an 800px image comes
    back at 800px. Emitting it would give the browser two candidates for one
    file, one of them under a descriptor that is a lie.
    """
    panel = panel_for(narrow_image)
    candidates = panel['srcset'].split(', ')
    assert len(candidates) == 1
    assert candidates[0].endswith('800w')


def test_sizes_describes_the_shorter_axis(narrow_image):
    """
    The panel is the viewport and the photo fits whichever axis runs out first,
    so 100vw alone would overstate the need on a height-limited photo.
    """
    # 800x600 is a 4:3 photo, so it runs out of height at 133vh
    assert panel_for(narrow_image)['sizes'] == 'min(100vw, 133vh)'


def test_download_points_at_the_uploaded_file(wide_image):
    """
    Display goes through renditions so the rungs cannot disagree about
    orientation, but 'download original' should hand over what was uploaded.
    """
    panel = panel_for(wide_image)
    assert panel['download'] == wide_image.file.url
    assert 'width-' not in panel['download']


def test_alt_text_falls_back_to_the_image_description(wide_image):
    slides = slides_for(wide_image)
    assert _slide_panel(slides, 0, 1, 'abcdefg')['alt_text'] == 'a description'

    slides[0]['alt_text'] = 'something specific'
    assert _slide_panel(slides, 0, 1, 'abcdefg')['alt_text'] == 'something specific'


# ---------------------------------------------------------------------------
# the three-up window
# ---------------------------------------------------------------------------

@pytest.fixture
def gallery(db):
    """
    A GalleryPage holding one SlidesBlock of four slides.
    """
    images = [make_image(title=f'slide {i}') for i in range(4)]
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
    # under the site's root page, not the tree root: a page outside a site has
    # no URL at all, which would quietly hollow out the close-link assertions
    Site.objects.get(is_default_site=True).root_page.add_child(instance=page)
    return page


@pytest.fixture
def client(db, settings):
    """
    zoom_slide 404s unless the host looks like the real site.
    """
    settings.ALLOWED_HOSTS = [*settings.ALLOWED_HOSTS, 'mahnamahna.test']
    return Client(SERVER_NAME='mahnamahna.test')


def slide_url(page, pos):
    return f'/slide/{page.id}/{BLOCK_ID[:7]}/{pos}'


def panels_in(response):
    return response.context['panels']


def test_middle_slide_gets_a_full_window(client, gallery):
    response = client.get(slide_url(gallery, 1))
    assert response.status_code == 200
    assert [p['pos'] for p in panels_in(response)] == [0, 1, 2]
    assert response.context['current_index'] == 1


def test_first_slide_has_no_previous_panel(client, gallery):
    """
    The window shrinks rather than padding, so the track has nothing to the left
    and overscroll says so.
    """
    response = client.get(slide_url(gallery, 0))
    assert [p['pos'] for p in panels_in(response)] == [0, 1]
    assert response.context['current_index'] == 0
    assert response.context['prev'] is None


def test_last_slide_has_no_next_panel(client, gallery):
    response = client.get(slide_url(gallery, 3))
    assert [p['pos'] for p in panels_in(response)] == [2, 3]
    assert response.context['current_index'] == 1
    assert response.context['next'] is None


def test_out_of_range_position_is_404(client, gallery):
    assert client.get(slide_url(gallery, 4)).status_code == 404
    assert client.get(slide_url(gallery, 99)).status_code == 404


def test_counter_counts_from_one(client, gallery):
    response = client.get(slide_url(gallery, 2))
    assert response.context['counter'] == 3
    assert response.context['total'] == 4


# ---------------------------------------------------------------------------
# the rendered lightbox
# ---------------------------------------------------------------------------

def test_only_the_current_panel_ships_a_loadable_image(client, gallery):
    """
    Neighbors are inert until lightbox.js hands them their sources, so a
    visitor without js -- who is shown one image, not a track -- is not billed
    for two extra originals.
    """
    html = client.get(slide_url(gallery, 1)).content.decode()
    assert html.count('<img src=') == 1
    assert html.count('<img data-src=') == 2


def test_current_panel_is_marked_for_the_nojs_layout(client, gallery):
    html = client.get(slide_url(gallery, 1)).content.decode()
    assert html.count('lightbox-panel is-current') == 1


def test_captions_travel_with_their_own_panel(client, gallery):
    """
    Each panel carries its caption, so dragging brings the next image and its
    caption in together -- and nothing has to update one on scroll.
    """
    html = client.get(slide_url(gallery, 1)).content.decode()
    for i in (0, 1, 2):
        assert f'caption {i}' in html
    assert 'caption 3' not in html


def test_close_link_is_relative(client, gallery):
    """
    Page.url has no request to tell it which Site is being browsed, and with more
    than one in the database it answers with an absolute URL -- which sends the
    close button to production from dev, from staging, from anywhere.
    """
    response = client.get(slide_url(gallery, 1))
    parent = response.context['parent_link']
    assert parent.startswith('/')
    assert '://' not in parent
    assert f'href="{parent}"' in response.content.decode()


def test_navigation_links_stay_inside_the_layer(client, gallery):
    """
    Prev/next are real links -- they are what a nojs visitor uses, and what
    lightbox.js follows once a swipe settles -- but they must not open a second
    overlay on top of this one.
    """
    html = client.get(slide_url(gallery, 1)).content.decode()
    navs = re.findall(r'<a class="lightbox-nav[^>]*>', html)
    assert len(navs) == 2
    assert all('up-layer="current"' in nav for nav in navs)
    assert slide_url(gallery, 0) in html
    assert slide_url(gallery, 2) in html


def test_the_lightbox_leaves_no_history_entries(client, gallery):
    """
    Unpoly would push an entry per slide, turning Back into a walk through
    everything just looked at. Instead lightbox.js takes over the entry the
    lightbox was opened on and rewrites it, so Back leaves the post outright.
    """
    response = client.get(slide_url(gallery, 1))
    html = response.content.decode()
    for nav in re.findall(r'<a class="lightbox-(?:nav|jump)[^>]*>', html):
        assert 'up-history="false"' in nav
    assert f'data-url="{slide_url(gallery, 1)}"' in html


def test_close_button_is_a_link_rather_than_a_dismisser(client, gallery):
    """
    Without js it has to be the way out; with js lightbox.js intercepts it.
    """
    response = client.get(slide_url(gallery, 1))
    html = response.content.decode()
    close = re.search(r'<a class="lightbox-button lightbox-close[^>]*>', html).group()
    assert 'up-dismiss' not in close
    assert f'href="{response.context["parent_link"]}"' in close


def test_lightbox_can_address_slides_outside_the_window(client, gallery):
    """
    A held-down arrow key jumps straight to its destination rather than walking
    there, which means addressing a slide the three-up window does not contain.
    """
    response = client.get(slide_url(gallery, 1))
    template = response.context['url_template']
    assert template.format(pos=3) == slide_url(gallery, 3)
    assert response.context['pos'] == 1
    assert f'data-url-template="{template}"' in response.content.decode()


# ---------------------------------------------------------------------------
# the same lightbox, for a single ImageBlock zoom
# ---------------------------------------------------------------------------

@pytest.fixture
def post_with_image(db):
    """
    A page holding one zoomable ImageBlock, captioned.
    """
    image = make_image(title='a zoomable image')
    page = ComplexPage(
        title='a post',
        slug='a-post',
        page_message='<p>hello</p>',
        body=json.dumps([{
            'type': 'image',
            'id': 'bbbbbbb1-2345-6789-abcd-ef0123456789',
            'value': {
                'image': image.id,
                'caption': '<p>what the picture shows</p>',
                'alt_text': 'how the picture is described',
                'link': '',
                'float': 0,
                'zoom': 1,
                'max_width': '',
            },
        }]),
    )
    Site.objects.get(is_default_site=True).root_page.add_child(instance=page)
    return page, image


def zoom_response(client, post_with_image):
    page, image = post_with_image
    return client.get(f'/zoom/img/{page.id}/{image.id}')


def test_image_zoom_renders_the_lightbox(client, post_with_image):
    response = zoom_response(client, post_with_image)
    assert response.status_code == 200
    html = response.content.decode()
    assert 'class="lightbox"' in html
    assert 'up-lightbox-download' in html  # the chrome a lone image still wants
    assert 'up-lightbox-fullscreen' in html


def test_image_zoom_has_a_window_of_one(client, post_with_image):
    response = zoom_response(client, post_with_image)
    assert len(response.context['panels']) == 1
    assert response.context['total'] == 1
    assert response.context['prev'] is None
    assert response.context['next'] is None


def test_image_zoom_drops_the_sequence_chrome(client, post_with_image):
    """
    Nothing to count through, play through, or navigate to -- and no jump link,
    which would otherwise be an anchor with no URL pattern behind it.
    """
    html = zoom_response(client, post_with_image).content.decode()
    assert 'up-lightbox-slideshow' not in html
    assert 'up-lightbox-counter' not in html
    assert 'lightbox-nav' not in html
    assert 'lightbox-jump' not in html


def test_image_zoom_leaves_the_caption_to_the_post(client, post_with_image):
    """
    An ImageBlock's caption is shown beneath the thumbnail on the post itself,
    so repeating it over the zoomed image would be saying it twice. A slide's
    caption is different: the lightbox is the only place it appears.
    """
    html = zoom_response(client, post_with_image).content.decode()
    assert 'what the picture shows' not in html
    assert '<figcaption>' not in html


def test_image_zoom_takes_its_alt_text_from_the_block(client, post_with_image):
    """
    The zoom URL names the image, not the block, so the view looks the block up
    to describe the zoomed image the way the thumbnail is described.
    """
    page, image = post_with_image
    panel = zoom_response(client, post_with_image).context['current']
    assert panel['alt_text'] == 'how the picture is described'


def test_image_zoom_offers_the_same_srcset_ladder(client, post_with_image):
    panel = zoom_response(client, post_with_image).context['current']
    assert panel['srcset'].endswith('w')
    assert panel['download'].endswith('.png')


def test_image_zoom_close_link_is_relative(client, post_with_image):
    parent = zoom_response(client, post_with_image).context['parent_link']
    assert parent.startswith('/')
    assert '://' not in parent


@pytest.fixture
def blog_post_with_image(db):
    """
    A blog post, whose canonical URL is date-prefixed rather than the tree path.
    """
    image = make_image(title='an image in a post')
    index = BlogIndex(title='blog', slug='blog', page_message='<p>the blog</p>')
    Site.objects.get(is_default_site=True).root_page.add_child(instance=index)
    post = ModernPost(
        title='a dated post',
        slug='a-dated-post',
        first_published_at=dt.datetime(2026, 5, 4, tzinfo=dt.timezone.utc),
        body=json.dumps([
            {
                'type': 'image',
                'id': 'ccccccc1-2345-6789-abcd-ef0123456789',
                'value': {
                    'image': image.id, 'caption': '', 'alt_text': '',
                    'link': '', 'float': 0, 'zoom': 1, 'max_width': '',
                },
            },
            {
                'type': 'slides',
                'id': BLOCK_ID,
                'value': {'slides': [
                    {'image': image.id, 'caption': '', 'alt_text': ''},
                ]},
            },
        ]),
    )
    index.add_child(instance=post)
    return post, image


def test_close_link_skips_the_redirect_to_a_post(client, blog_post_with_image):
    """
    A blog post's canonical URL is date-prefixed, and that lives on the specific
    class. Look it up on the base Page and you get the tree path, which merely
    301s to the real one -- so closing would spend a redirect getting home, and
    the address bar would settle on a URL the site does not consider canonical.
    """
    post, image = blog_post_with_image
    expected = post.get_url()

    zoom = client.get(f'/zoom/img/{post.id}/{image.id}')
    assert zoom.context['parent_link'] == expected

    slide = client.get(f'/slide/{post.id}/{BLOCK_ID[:7]}/0')
    assert slide.context['parent_link'] == expected

    assert '/2026/05/' in expected
    assert client.get(expected).status_code == 200
