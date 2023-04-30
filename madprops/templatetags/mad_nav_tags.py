from django import template
from wagtail.models import Page, Site

register = template.Library()


@register.inclusion_tag('madprops/tags/nav.html', takes_context=True)
def mad_props_nav(context, home, calling_page=None):
    current_site = Site.find_for_request(context['request'])
    menuitems = Page.objects.in_site(current_site).live().in_menu().specific()
    for menuitem in menuitems:
        if (
            menuitem.get_content_type().model == 'homepage'
        ):
            menuitem.title = 'Current Edition'
            menuitem.active = context.get('theres_no_place_like_home')
        elif (
            menuitem.get_content_type().model == 'archivespage'
        ):
            menuitem.active = (
                calling_page.url_path.startswith(menuitem.url_path)
                if calling_page else False
            ) or (
                calling_page.content_type.model == 'editionpage'
                and not context.get('theres_no_place_like_home')
            )
        else:
            menuitem.active = (
                calling_page.url_path.startswith(menuitem.url_path)
                if calling_page else False
            )
    return {
        'calling_page': calling_page,
        'menuitems': menuitems,
        'request': context['request'],
    }
