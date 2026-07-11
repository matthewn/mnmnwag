"""
Tests for the custom ImageBlock and its template (mnmnwag/blocks/image_block.html).

The block exposes seven fields -- image, alt_text, caption, link, float, zoom,
max_width --
and the template branches on most of them. These tests render the block the way
Wagtail does when loading stored content (`to_python` from the StreamField JSON)
and assert the resulting markup.
"""
import pytest
from wagtail.images import get_image_model
from wagtail.images.tests.utils import get_test_image_file

from mnmnwag.blocks import FloatChoices, ImageBlock, ZoomChoices


@pytest.fixture
def test_image(db):
    return get_image_model().objects.create(
        title="test image",
        description="a description",
        file=get_test_image_file(),
    )


def render_block(
    image,
    *,
    caption="",
    alt_text="",
    link="",
    float_=FloatChoices.NONE.value,
    zoom=ZoomChoices.ON.value,
    max_width="",
):
    """Render ImageBlock as Wagtail does when loading stored content.

    `to_python` mirrors loading from the StreamField JSON, where the choice
    fields are stored -- and arrive -- as integers.
    """
    block = ImageBlock()
    value = block.to_python({
        "image": image.id,
        "caption": caption,
        "alt_text": alt_text,
        "link": link,
        "float": float_,
        "zoom": zoom,
        "max_width": max_width,
    })
    return block.render(value, context={"page_id": 1})


# ---------------------------------------------------------------------------
# premise: the choice fields reach the template as integers
# ---------------------------------------------------------------------------

def test_choice_fields_deserialize_to_integers():
    """
    If this ever changes, the int-vs-string comparisons in the template
    (and the regressions they guard against) stop being the relevant concern.
    """
    block = ImageBlock()
    assert block.child_blocks["zoom"].to_python(1) == 1
    assert block.child_blocks["zoom"].to_python(1) != "1"
    assert block.child_blocks["float"].to_python(2) == 2
    assert block.child_blocks["float"].to_python(2) != "2"


# ---------------------------------------------------------------------------
# image rendition
# ---------------------------------------------------------------------------

def test_image_rendered_at_width_800(test_image):
    html = render_block(test_image)
    assert "<img " in html
    assert "width-800" in html  # the rendition spec from {% image ... width-800 %}


# ---------------------------------------------------------------------------
# alt text
# ---------------------------------------------------------------------------

def test_alt_text_used_when_present(test_image):
    html = render_block(test_image, alt_text="a fancy hat")
    assert 'alt="a fancy hat"' in html


def test_alt_text_falls_back_to_image_description(test_image):
    # test_image.description == "a description"
    html = render_block(test_image, alt_text="")
    assert 'alt="a description"' in html


# ---------------------------------------------------------------------------
# caption
# ---------------------------------------------------------------------------

def test_caption_rendered_when_present(test_image):
    html = render_block(test_image, caption="<p>Sunset</p>")
    assert '<figcaption class="caption">' in html
    assert "Sunset" in html
    assert "</figcaption>" in html


def test_no_caption_when_absent(test_image):
    html = render_block(test_image, caption="")
    assert "<figcaption" not in html


# ---------------------------------------------------------------------------
# float
# ---------------------------------------------------------------------------

def test_float_left(test_image):
    html = render_block(test_image, float_=FloatChoices.LEFT.value)
    assert '<figure class="float left">' in html


def test_float_right(test_image):
    html = render_block(test_image, float_=FloatChoices.RIGHT.value)
    assert '<figure class="float right">' in html


def test_float_none_has_no_float_class(test_image):
    html = render_block(test_image, float_=FloatChoices.NONE.value)
    assert "<figure>" in html
    assert "float" not in html


# ---------------------------------------------------------------------------
# max_width
# ---------------------------------------------------------------------------

def test_max_width_sets_custom_property(test_image):
    # any valid CSS max-width value is passed through verbatim
    html = render_block(test_image, max_width="30%")
    assert '<figure style="--max-width: 30%;">' in html


def test_max_width_pixels(test_image):
    html = render_block(test_image, max_width="320px")
    assert "--max-width: 320px;" in html


def test_max_width_coexists_with_float(test_image):
    html = render_block(test_image, float_=FloatChoices.LEFT.value, max_width="20rem")
    assert '<figure class="float left" style="--max-width: 20rem;">' in html


def test_no_max_width_leaves_figure_unstyled(test_image):
    # existing blocks (no max_width) must render with no style attribute
    html = render_block(test_image, max_width="")
    assert "style=" not in html
    assert "--max-width" not in html


# ---------------------------------------------------------------------------
# zoom
# ---------------------------------------------------------------------------

def test_zoom_on_wraps_image_in_zoom_link(test_image):
    html = render_block(test_image, zoom=ZoomChoices.ON.value)
    # the image must be wrapped in the unpoly zoom modal link
    assert f'href="/zoom/img/1/{test_image.id}"' in html
    assert 'up-layer="new modal"' in html
    # anchors must balance
    assert html.count("<a ") == 1
    assert html.count("</a>") == 1


def test_zoom_off_has_no_zoom_link(test_image):
    html = render_block(test_image, zoom=ZoomChoices.OFF.value)
    assert "/zoom/img/" not in html
    # no anchor at all, and crucially no orphaned closing tag
    assert "<a " not in html
    assert "</a>" not in html


# ---------------------------------------------------------------------------
# link (and its precedence over zoom)
# ---------------------------------------------------------------------------

def test_plain_link_wraps_image(test_image):
    html = render_block(test_image, link="http://example.com/page", zoom=ZoomChoices.OFF.value)
    assert '<a href="http://example.com/page">' in html
    assert "up-layer" not in html  # a plain link, not the zoom modal
    assert html.count("<a ") == 1
    assert html.count("</a>") == 1


def test_link_takes_precedence_over_zoom(test_image):
    # when both are set the template uses the plain link, not the zoom modal
    html = render_block(test_image, link="http://example.com/page", zoom=ZoomChoices.ON.value)
    assert '<a href="http://example.com/page">' in html
    assert "/zoom/img/" not in html
    assert "up-layer" not in html
    assert html.count("<a ") == 1
    assert html.count("</a>") == 1
