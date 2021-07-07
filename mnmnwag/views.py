from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.safestring import mark_safe

from .models import CustomImage

import datetime as dt
import os


def theme_picker(request, chosen_theme):
    try:
        destination = request.META['HTTP_REFERER']
    except KeyError:
        destination = request.META['HTTP_HOST'] + '/blog'
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


def zoom_image(request, image_id):
    """
    "Zoom" (on-page popup, really) an image, given an ID.
    """
    img = CustomImage.objects.get(id=image_id)
    return render(request, 'mnmnwag/zoom.html', {
        'img': img,
    })


def zoom_slides(request, img_set, pos):
    """
    "Zoom" (on-page popup, usually) an image set, given a comma-separated
    set of image IDs, and an integer indicating our position in the slideshow.
    """
    pos = int(pos)
    img_list = img_set.split(',')
    img = CustomImage.objects.get(id=img_list[pos])
    next_pos = ''
    prev_pos = ''

    if pos < len(img_list) - 1:
        next_pos = pos + 1
    if pos > 0:
        prev_pos = pos - 1

    return render(request, 'mnmnwag/zoom.html', {
        'img': img,
        'img_set': img_set,
        'next_pos': str(next_pos),
        'prev_pos': str(prev_pos),
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
