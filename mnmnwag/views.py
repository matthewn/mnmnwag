from django.shortcuts import render

import os.path


def zoom(request, filepath):
    return render(request, 'mnmnwag/zoom.html', {
        'filepath': filepath,
        'filename': os.path.basename(filepath),
    })
