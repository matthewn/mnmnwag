from django.conf import settings
from django.urls import include
from django.contrib import admin
from django.urls import path
from django.views.generic.base import RedirectView, TemplateView

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from search import views as search_views

from wagtail_footnotes import urls as footnotes_urls

from mnmnwag.feeds import LatestEntriesFeed
from mnmnwag.views import theme_picker, zoom_image, zoom_old, zoom_slide

from subs.views import sub_create, sub_confirm, sub_remove


urlpatterns = [
    path(
        'robots.txt',
        TemplateView.as_view(template_name='robots.txt', content_type='text/plain'),
    ),
    path(
        'favicon.ico',
        RedirectView.as_view(
            url=settings.STATIC_URL + 'img/favs/favicon-32x32.png',
            permanent=True,
        ),
    ),
    path('dja/', admin.site.urls),
    path('cms/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),

    path('likes/', include('likes.urls')),

    path('comments/', include('django_comments_xtd.urls')),
    path("footnotes/", include(footnotes_urls)),
    path('__reload__/', include('django_browser_reload.urls')),

    path('search/', search_views.search, name='search'),
    path('zoom/img/<int:page_id>/<int:image_id>', zoom_image, name='zoom_image'),
    path('slide/<int:page_id>/<str:block_id>/<int:pos>', zoom_slide, name='zoom_slide'),
    path('zoom/old/<path:image_path>', zoom_old, name='zoom_old'),
    path('theme/<str:chosen_theme>', theme_picker, name='theme_picker'),
    # path('showinfo/', show_info, name='show_info'),

    path('sub/create', sub_create, name='sub_create'),
    path('sub/<str:uuid>/confirm', sub_confirm, name='sub_confirm'),
    path('sub/<str:uuid>/remove', sub_remove, name='sub_remove'),

    path('events/', include('seevooplay.urls')),

    path('blog/feed/<str:tag_ids>/', LatestEntriesFeed(), name='feed_tags'),
    path('blog/feed/', LatestEntriesFeed(), name='feed'),

    path('', include(wagtail_urls)),
]

handler404 = 'mnmnwag.views.handler404'
handler500 = 'mnmnwag.views.handler500'

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    urlpatterns = [
        path('__debug__/', include('debug_toolbar.urls')),
    ] + urlpatterns
