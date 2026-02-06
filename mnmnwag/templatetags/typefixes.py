from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from typogrify.templatetags.typogrify_tags import smartypants, typogrify

from mnmnwag.utils import get_site

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
    return mark_safe(text)


@register.filter(is_safe=True)
@stringfilter
def typefixes_minimal(text):
    """
    A version of the typefixes filter that only applies smartypants instead of
    the whole typogrify suite of fixes.
    """
    # unescape characters from wagtail richtext filter
    text = text.replace('&quot;', '"')
    text = text.replace('&#x27;', "'")

    text = smartypants(text)

    text = alumyears(text)
    return mark_safe(text)


@register.filter
@stringfilter
def namecloak(text):
    site = get_site()
    if site == 'mnmnwag':
        return mark_safe(
            text.replace('Matthew Newton', r'<span class="mahna">/\/\/\/</span>')
        )
    if site == 'madprops':
        return text.replace('Matthew Newton', 'The Mad Propster')
