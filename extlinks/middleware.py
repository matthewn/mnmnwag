from django.conf import settings
import re


ignore_domains = getattr(settings, 'EXTLINKS_IGNORE_DOMAINS', ())
templates_whitelist = getattr(settings, 'EXTLINKS_TEMPLATES_WHITELIST', ())


class RewriteExternalLinksMiddleware(object):
    """
    Rewrite all external links to open in a new tab/window.
    (A somewhat (?) naive implementation, expected to improve over time.)

    Rewrite:
        <a href="http://www.example.com">
    To:
        <a target="_blank" href="http://www.example.com">
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        if response.streaming:
            return response

        if not templates_whitelist:
            return response

        link_regex = re.compile('<\s*a[^>]*>')
        new_content = response.rendered_content
        ignore_strings = ['://' + domain for domain in ignore_domains]

        try:
            matches = link_regex.findall(new_content)
        except TypeError:
            return response

        if any(path in response.template_name for path in templates_whitelist):
            for match in matches:
                if all(item not in match for item in ignore_strings):
                    if '://' in match and 'target=' not in match:
                        new_link = match.replace(' href=', ' target="_blank" href=')
                        new_content = new_content.replace(match, new_link, 1)

        response.content = new_content

        return response
