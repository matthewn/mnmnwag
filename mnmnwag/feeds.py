from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from .models import BlogIndex


class LatestEntriesFeed(Feed):
    feed_type = Atom1Feed
    title = "mahnamahna.net/blog"
    link = "/rss/"
    subtitle = "The latest blog posts from mahnamahna.net."

    def items(self):
        index = BlogIndex.objects.get()
        return index.get_posts()[:2]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.specific.body

    def item_link(self, item):
        return item.specific.get_absolute_url()
