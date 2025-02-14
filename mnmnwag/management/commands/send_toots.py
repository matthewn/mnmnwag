from django.conf import settings
from django.core.management.base import BaseCommand
from mnmnwag.models import ModernPost, TootsTracker
from mastodon import Mastodon

import logger


class Command(BaseCommand):
    help = 'Post links to new posts on Mastodon'

    def handle(self, *args, **options):
        tracker = TootsTracker.load()
        posts = ModernPost.objects.live().public().filter(
            first_published_at__gte=tracker.last_run_at
        )

        if posts:
            mastodon_keys = settings.MASTODON_AUTH_KEYS

            mastodon = Mastodon(
                access_token=mastodon_keys['access_token'],
                api_base_url=mastodon_keys['api_base_url']
            )

            for post in posts:
                if post.toot_this:
                    if post.toot_text:
                        title = post.toot_text
                    else:
                        if 'micro' in post.tags.names():
                            title = post.micropost_title
                        else:
                            title = post.title
                    link = post.full_url
                    content = f'{title} {link}'
                    try:
                        mastodon.toot(content)
                        logger.info(f'Successfully posted to Mastodon: {content}')
                    except Exception as e:
                        logger.error(f'Error posting to Mastodon: {e}')

            tracker.save()
