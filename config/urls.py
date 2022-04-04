from django.conf import settings
from django.conf.urls import include, url
from django.urls import path
from django.contrib import admin

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from search import views as search_views

from mnmnwag.feeds import LatestEntriesFeed
from mnmnwag.views import theme_picker, zoom_image, zoom_old, zoom_slide

from seevooplay.views import email_guests, event_page
from subs.views import sub_create, sub_confirm, sub_remove


urlpatterns = [
    url(r'^dja/', admin.site.urls),
    url(r'^cms/', include(wagtailadmin_urls)),
    url(r'^documents/', include(wagtaildocs_urls)),

    url(r'^comments/', include('django_comments_xtd.urls')),

    path('__reload__/', include('django_browser_reload.urls')),

    url(r'^search/$', search_views.search, name='search'),
    path('zoom/img/<int:page_id>/<int:image_id>', zoom_image, name='zoom_image'),
    path('slide/<int:page_id>/<str:block_id>/<int:pos>', zoom_slide, name='zoom_slide'),
    path('zoom/old/<path:image_path>', zoom_old, name='zoom_old'),
    path('theme/<str:chosen_theme>', theme_picker, name='theme_picker'),

    path('sub/create', sub_create, name='sub_create'),
    path('sub/<str:uuid>/confirm', sub_confirm, name='sub_confirm'),
    path('sub/<str:uuid>/remove', sub_remove, name='sub_remove'),

    path('dja/email_guests/<int:event_id>/', email_guests, name='email_guests'),
    path('rsvp/<int:event_id>/', event_page, name='invitation'),
    path('rsvp/<int:event_id>/<guest_uuid>/', event_page),
    path('djrichtextfield/', include('djrichtextfield.urls')),

    url(r'^blog/feed/', LatestEntriesFeed(), name='feed'),

    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    url(r'', include(wagtail_urls)),

    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    url(r'^pages/', include(wagtail_urls)),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
