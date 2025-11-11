from django import template

import secrets
import string

register = template.Library()


@register.simple_tag
def prefix():
    """
    Return e.g. "acwk-" or "ctbc-" as a reusable prefix for HTML class names.
    """
    return ''.join(secrets.choice(string.ascii_lowercase) for _ in range(4)) + '-'
