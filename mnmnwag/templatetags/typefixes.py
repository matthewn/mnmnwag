from django import template
from django.template.defaultfilters import stringfilter
from typogrify.templatetags.typogrify_tags import typogrify

import re

register = template.Library()


@register.filter(is_safe=True)
@stringfilter
def alumyears(value):
    """ Fix apostrophes before alumni year. """
    regex = re.compile(" ('|‘|&#8216;)(\\d\\d)")
    value = regex.sub(' ’\\g<2>', value)
    return value


@register.filter(is_safe=True)
@stringfilter
def typefixes(text):
    # unescape characters from wagtail richtext filter
    text = text.replace('&quot;', '"')
    text = text.replace('&#x27;', "'")

    text = typogrify(text)
    text = alumyears(text)
    return text
