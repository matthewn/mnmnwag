from django.conf import settings
from django.conf.urls import include, url
from django.urls import path
from django.contrib import admin

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from search import views as search_views

from mnmnwag.feeds import LatestEntriesFeed
from mnmnwag.views import theme_picker, zoom


urlpatterns = [
    url(r'^dja/', admin.site.urls),

    url(r'^cms/', include(wagtailadmin_urls)),
    url(r'^documents/', include(wagtaildocs_urls)),

    url(r'^comments/', include('django_comments_xtd.urls')),

    url(r'^search/$', search_views.search, name='search'),
    path('zoom/img/<int:image_id>', zoom, name='zoom'),
    path('theme/<str:chosen_theme>', theme_picker, name='theme_picker'),

    url(r'^blog/feed/', LatestEntriesFeed()),

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
