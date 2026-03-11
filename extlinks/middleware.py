from django.conf import settings
import re


ignore_domains = getattr(settings, 'EXTLINKS_IGNORE_DOMAINS', ())
templates_whitelist = getattr(settings, 'EXTLINKS_TEMPLATES_WHITELIST', ())

link_regex = re.compile(r'<\s*a[^>]*>')
ignore_strings = ['://' + domain for domain in ignore_domains]


class RewriteExternalLinksMiddleware(object):
    """
    Rewrite all external links to open in a new tab/window.
    (In which we commit a sin by altering HTML with a regex -- but it's okay! Really!)

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

        if not any(path in response.template_name for path in templates_whitelist):
            return response

        response.add_post_render_callback(self._rewrite_links)
        return response

    @staticmethod
    def _rewrite_links(response):
        content = response.content.decode(response.charset)
        for match in link_regex.findall(content):
            if all(item not in match for item in ignore_strings):
                if '://' in match and 'target=' not in match:
                    new_link = match.replace(' href=', ' target="_blank" href=')
                    content = content.replace(match, new_link, 1)
        response.content = content
