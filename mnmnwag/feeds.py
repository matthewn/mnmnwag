from dateutil import tz
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from .models import BlogIndex


class LatestEntriesFeed(Feed):
    feed_type = Atom1Feed
    title = 'mahnamahna.net/blog'
    link = '/blog/feed'
    subtitle = 'The latest blog posts from mahnamahna.net.'

    def items(self):
        index = BlogIndex.objects.get()
        return index.get_posts()[:15]

    def item_title(self, item):
        if 'micro' in item.specific.tags.names():
            home_zone = tz.gettz('America/Los_Angeles')
            post_date = item.first_published_at.astimezone(home_zone).strftime('%Y-%m-%d %I:%M %p')
            return f'micropost ({post_date})'
        else:
            return item.title

    def item_description(self, item):
        return item.specific.body

    def item_link(self, item):
        return item.specific.get_absolute_url()
