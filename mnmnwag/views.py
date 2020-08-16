from django.shortcuts import render

from wagtail.images.models import Image


def zoom(request, image_id):
    img = Image.objects.get(id=image_id)
    return render(request, 'mnmnwag/zoom.html', {
        'img': img,
    })
