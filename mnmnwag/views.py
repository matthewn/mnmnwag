from django.http import HttpResponseRedirect
from django.shortcuts import render

from .models import CustomImage

import datetime as dt


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
    img = CustomImage.objects.get(id=image_id)
    return render(request, 'mnmnwag/zoom.html', {
        'img': img,
    })
