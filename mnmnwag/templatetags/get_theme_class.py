from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def get_theme_class(context):
    """
    Return theme class string for use on <body> tag.

    Use stored value if cookie is set, otherwise follow the system setting.
    """
    try:
        request = context['request']
        theme = (
            request.META.get('HTTP_X_THEME_CLASS')
            or request.COOKIES.get('themeClass')
            or 'theme-system'
        )
    except KeyError:
        theme = 'theme-system'
    # system resolves to light here; a pre-paint script swaps in dark if preferred
    return f'{theme} theme-light' if theme == 'theme-system' else theme
