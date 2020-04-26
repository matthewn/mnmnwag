from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter(is_safe=True)
@stringfilter
def is_numeric(value):
    """Remove True if value is numeric."""
    return "{}".format(value).isdigit()
