from django.conf import settings
from django.core.management.base import BaseCommand
# from django.core.mail import send_mail

from mnmnwag.models import ModernPost, TweetsTracker

import tweepy


class Command(BaseCommand):
    help = 'tweet links to new posts'

    def handle(self, *args, **options):
        tracker = TweetsTracker.load()
        auth_keys = settings.TWITTER_AUTH_KEYS
        posts = ModernPost.objects.live().public().filter(
            first_published_at__gte=tracker.last_run_at
        )
        if posts:
            # methodology taken from:
            # https://www.mattcrampton.com/blog/step_by_step_tutorial_to_post_to_twitter_using_python/
            auth = tweepy.OAuthHandler(
                auth_keys['consumer_key'],
                auth_keys['consumer_secret'],
            )
            auth.set_access_token(
                auth_keys['access_token'],
                auth_keys['access_token_secret']
            )
            api = tweepy.API(auth)
            for post in posts:
                if post.do_not_tweet is False:
                    if post.tweet_title:
                        title = post.tweet_title
                    else:
                        if 'micro' in post.tags.names():
                            title = post.micropost_title
                        else:
                            title = post.title
                    link = post.full_url
                    tweet = f'{title} {link}'
                    status = api.update_status(status=tweet)  # noqa F841
                    # send_mail(f'mnmnwag: posted tweet {status["id_str"]} [eom]', '', None, [settings.ADMINS[0][1]])
            tracker.save()
