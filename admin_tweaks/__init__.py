""" Add a custom .css hook to tweak Wagtail's admin area. """
from django.templatetags.static import static
from django.utils.html import format_html

from wagtail.core import hooks


@hooks.register('insert_global_admin_css', order=100)
def global_admin_css():
    """ Add /static/admin_tweaks/wagtail.css. """
    return format_html('<link rel="stylesheet" href="{}">', static("admin_tweaks/wagtail.css"))
