from django import template
from threading import local

register = template.Library()
_thread_state = local()


@register.simple_tag(takes_context=True)
def prefix(context, scope='c'):
    """
    Returns a sequential string suitable for use as an HTML class or ID.
    Scopes are independent within a request, e.g.:

        {% prefix "a" %} → a1, a2, ...
        {% prefix "b" %} → b1, b2, ...

    The counters reset each request.
    """
    request = context.get('request')
    target = request if request is not None else _thread_state

    # get or create a dict of counters for this request/thread
    counters = getattr(target, '_prefix_counters', None)
    if counters is None:
        counters = {}
        setattr(target, '_prefix_counters', counters)

    # increment the counter for this scope
    counters[scope] = counters.get(scope, 0) + 1
    return f'{scope}{counters[scope]}-'
