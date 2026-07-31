from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.safestring import mark_safe
from wagtail.models import Page

from .models import CustomImage
from .utils import get_client_ip

import datetime as dt
import os
import sys


def handler404(request, exception, template_name='404.html'):
    if 'madprops' in request.get_host():
        context = {
            'override_base': 'madprops/base.html',
            'msg': 'We don’t have that here.',
        }
    else:
        context = {'msg': 'NO CAN FIND, MAHN.'}
    response = render(request, template_name, context)
    response.status_code = 404
    return response


def handler403(request, exception, template_name='403.html'):
    if 'madprops' in request.get_host():
        context = {'override_base': 'madprops/base.html'}
    else:
        context = {}
    response = render(request, template_name, context)
    response.status_code = 403
    return response


def handler500(request, *args, **argv):
    if 'madprops' in request.get_host():
        context = {
            'override_base': 'madprops/base.html',
        }
    else:
        context = {}
    response = render(request, '500.html', context)
    response.status_code = 500
    return response


def theme_picker(request, chosen_theme):
    try:
        destination = request.headers['referer']
    except KeyError:
        destination = f'{request.scheme}://{request.headers["host"]}'
    response = HttpResponseRedirect(destination)
    if chosen_theme in ('light', 'dark', 'retro'):
        theme_class = f'theme-{chosen_theme}'
        expires = dt.datetime.now(tz=dt.timezone.utc) + dt.timedelta(days=365)
        response.set_cookie(
            'themeClass',
            value=theme_class,
            expires=expires,
            samesite='strict',
            secure=not settings.DEBUG,
        )
    return response


SLIDE_SMALL_WIDTH = 1200
SLIDE_LARGE_WIDTH = 2800

# a position no gallery will ever hold, so reversing with it yields a URL whose
# position component can be swapped for a placeholder unambiguously
_POS_SENTINEL = 987654321


def _lightbox_panel(image, caption, alt_text, url, pos):
    """
    Build the context for one panel of the lightbox.

    Each panel carries its own srcset so phones can take a rendition rather than
    the original: a slide's lightbox holds prev/current/next in the DOM at once
    (see lightbox.js), so it costs three images, and on a photo here that is
    three times several megabytes.
    """
    original = image.get_rendition('original')

    # Two rungs, neither of them the original: past the small one the only
    # candidate left would be a multi-megabyte file, which is what a phone in
    # landscape would end up fetching. The download button still links it whole.
    # Wagtail will not upscale, so the large rung stops at the original's own
    # width, and the small one is dropped once it is no longer a real saving --
    # otherwise both would name one file, one of them under a lying descriptor.
    large = min(original.width, SLIDE_LARGE_WIDTH)
    widths = [SLIDE_SMALL_WIDTH, large] if SLIDE_SMALL_WIDTH * 1.2 < large else [large]
    renditions = [image.get_rendition(f'width-{w}') for w in widths]

    # What the CSS actually paints: the panel is the viewport, and the photo fits
    # whichever of its axes runs out first (see lightbox.css). Saying 100vw here
    # would overstate the need on a height-limited photo and buy a rung too many.
    sizes = f'min(100vw, {round(original.width / original.height * 100)}vh)'

    return {
        'pos': pos,
        'url': url,
        'src': renditions[-1].url,
        'srcset': ', '.join(f'{r.url} {r.width}w' for r in renditions),
        'sizes': sizes,
        # the lightbox sizes the photo from its panel, and caps it here so it is
        # never blown up past its own pixels
        'width': original.width,
        'height': original.height,
        'download': image.file.url,
        'filename': os.path.basename(image.file.name),
        'caption': caption,
        'alt_text': alt_text or image.description,
    }


def _image_block_for(page, image_id):
    """
    Find the ImageBlock on a page that shows a given image.

    Only for its alt text, so the zoomed image is described the same way the
    thumbnail is. The block's caption belongs to the post, where it is already
    shown beneath the thumbnail -- unlike a slide's caption, which has nowhere to
    live but the lightbox.

    The zoom URL identifies the image but not the block holding it, and the alt
    text lives on the block; rather than change a URL that is already out in the
    world, look the block up. An image used twice on one page takes the first
    block's alt text, which is the best guess available.
    """
    body = getattr(page, 'body', None) or []
    for block in body:
        if block.block_type != 'image':
            continue
        if block.value['image'] and block.value['image'].id == image_id:
            return block.value
    return None


def zoom_image(request, page_id, image_id):
    """
    "Zoom" a single image from an ImageBlock, given an ID.

    Renders the same lightbox a slide gets, with a window of exactly one panel:
    no neighbors to swipe to, so the template drops the counter, the slideshow
    and the prev/next arrows.
    """
    if 'mahnamahna' not in request.get_host():
        raise Http404
    page = Page.objects.get(id=page_id).specific  # see zoom_slide
    img = CustomImage.objects.get(id=image_id)
    block = _image_block_for(page, image_id)

    panel = _lightbox_panel(
        image=img,
        caption='',  # the post shows it; see _image_block_for
        alt_text=block['alt_text'] if block else '',
        url=request.path,
        pos=0,
    )

    return TemplateResponse(request, 'mnmnwag/lightbox.html', {
        'panels': [panel],
        'current': panel,
        'current_index': 0,
        'prev': None,
        'next': None,
        'counter': 1,
        'total': 1,
        'pos': 0,
        'url_template': '',
        'parent_link': page.get_url(request=request),  # relative; see zoom_slide
    })


def _slide_panel(slides, pos, page_id, block_id):
    """
    One panel of a SlidesBlock's lightbox, addressed by its position.
    """
    slide = slides[pos]
    return _lightbox_panel(
        image=slide['image'],
        caption=slide['caption'],
        alt_text=slide['alt_text'],
        url=reverse('zoom_slide', kwargs={
            'page_id': page_id,
            'block_id': block_id,
            'pos': pos,
        }),
        pos=pos,
    )


def zoom_slide(request, page_id, block_id, pos):
    """
    Display one slide from a SlidesBlock in a Page.

    page_id is the id of a Page containing one or more SlidesBlocks
    block_id is the 1st 7 characters of the uuid of the SlidesBlock to reference
    pos ('position') is a zero-based index of the slide to display

    The response carries three slides, not one: the slide asked for plus its
    neighbors, which the lightbox lays out side by side so a swipe can track
    the finger. Those neighbors double as the preload for wherever the swipe
    lands, so moving between slides costs one new image.
    """
    if 'mahnamahna' not in request.get_host():
        raise Http404
    page = Page.objects.get(id=page_id).specific
    body = page.body
    block = [b for b in body if b.id[0:7] == block_id][0]
    slides = block.value['slides']

    if not 0 <= pos < len(slides):
        raise Http404

    prev_pos = pos - 1 if pos > 0 else None
    next_pos = pos + 1 if pos < len(slides) - 1 else None
    window = [p for p in (prev_pos, pos, next_pos) if p is not None]
    panels = [_slide_panel(slides, p, page_id, block_id) for p in window]
    current_index = window.index(pos)

    # The window reaches one slide either way, so a held-down arrow key has to be
    # able to address a slide that is not in it. Hand the lightbox a pattern to
    # build those URLs from rather than have it assemble paths itself.
    url_template = reverse('zoom_slide', kwargs={
        'page_id': page_id,
        'block_id': block_id,
        'pos': _POS_SENTINEL,
    }).replace(str(_POS_SENTINEL), '{pos}')

    return TemplateResponse(request, 'mnmnwag/lightbox.html', {  # see zoom_image
        'panels': panels,
        'current': panels[current_index],
        'current_index': current_index,
        'prev': panels[0] if prev_pos is not None else None,
        'next': panels[-1] if next_pos is not None else None,
        'counter': pos + 1,
        'total': len(slides),
        'pos': pos,
        'url_template': url_template,
        # get_url over .url: with more than one Site in the database, .url cannot
        # tell which one is being browsed and answers with an absolute URL, which
        # would send the close button to production from anywhere
        'parent_link': page.get_url(request=request),
        'page_id': page_id,
        'block_id': block_id,
    })


def zoom_old(request, image_path):
    """
    Use the zoom template to display a LegacyPost's image, given a path.
    """
    if not image_path.startswith('media/legacy/images/blog/'):
        raise PermissionDenied

    # some legacy images have a .txt file right next door that
    # contains a caption. look for one and get its contents.
    caption_path = os.path.splitext(image_path)[0] + '.txt'
    caption_file = os.path.join(
        settings.MEDIA_ROOT.replace('media', ''),
        caption_path,
    )
    if os.path.exists(caption_file):
        with open(caption_file, 'r') as f:
            caption = f.read()
    else:
        caption = ''

    img = {}
    img['url'] = f'/{image_path}'
    img['filename'] = image_path.split('/')[-1]
    img['caption'] = mark_safe(caption)

    return render(request, 'mnmnwag/zoom.html', {
        'old_img': img,
    })


def show_info(request):
    """
    For debugging server-side config woe. Display some stuff we want to see.
    """
    content = f'<br>Python version: {sys.version}'
    content += f'<br>REMOTE_ADDR: {request.META.get("REMOTE_ADDR")}'
    content += f'<br>HTTP_X_FORWARDED_FOR: {request.headers.get("x-forwarded-for")}'
    content += f'<br>CLIENT_IP: {get_client_ip(request)}'
    return render(request, 'mnmnwag/showview.html', {
        'title': 'information!',
        'page_message': 'information!',
        'content': mark_safe(content),
    })


# def force403(request):
#     raise PermissionDenied


# def force500(request):
#     raise Exception('Deliberate 500 for testing the error page.')
