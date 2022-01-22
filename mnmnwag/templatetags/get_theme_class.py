from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def get_theme_class(context):
    """
    Return theme class string for use on <body> tag.

    Use stored value if cookie is set, otherwise provide default value.
    """
    request = context['request']
    try:
        theme = request.COOKIES['themeClass']
    except KeyError:
        theme = 'theme-light'  # default theme
    return theme
