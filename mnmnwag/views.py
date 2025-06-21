from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.utils.safestring import mark_safe
from wagtail.models import Page, Site

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
        site = Site.find_for_request(request)
        if site.is_default_site:
            destination = request.headers['host'] + '/blog'
        else:
            destination = request.headers['host']
    response = HttpResponseRedirect(destination)
    if chosen_theme in ('light', 'dark', 'retro'):
        theme_class = f'theme-{chosen_theme}'
        expires = dt.datetime.now(tz=dt.timezone.utc) + dt.timedelta(days=365)
        response.set_cookie(
            'themeClass',
            value=theme_class,
            expires=expires,
            samesite='strict',
        )
    return response


def zoom_image(request, page_id, image_id):
    """
    "Zoom" (on-page popup, really) an image, given an ID.
    """
    if 'mahnamahna' not in request.get_host():
        raise Http404
    page = Page.objects.get(id=page_id)
    img = CustomImage.objects.get(id=image_id)
    return render(request, 'mnmnwag/zoom.html', {
        'img': img,
        'parent_link': page.url,
    })


def zoom_slide(request, page_id, block_id, pos):
    """
    Display one slide from a SlidesBlock in a Page.

    page_id is the id of a Page containing one or more SlidesBlocks
    block_id is the 1st 8 digits of the uuid of the SlidesBlock to reference
    pos ('position') is a zero-based index of the slide to display
    """
    if 'mahnamahna' not in request.get_host():
        raise Http404
    page = Page.objects.get(id=page_id)
    body = page.specific.body
    block = [b for b in body if b.id[0:7] == block_id][0]
    slides = block.value['slides']

    next_pos = ''
    prev_pos = ''
    if pos < len(slides) - 1:
        next_pos = pos + 1
    if pos > 0:
        prev_pos = pos - 1

    return render(request, 'mnmnwag/slide.html', {
        'img': slides[pos]['image'],
        'caption': slides[pos]['caption'],
        'alt_text': slides[pos]['alt_text'],
        'parent_link': page.url,
        'next_pos': str(next_pos),
        'prev_pos': str(prev_pos),
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
