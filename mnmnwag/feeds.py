from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from .models import BlogIndex
from .utils import get_micropost_title


class LatestEntriesFeed(Feed):
    feed_type = Atom1Feed
    title = 'mahnamahna.net/blog'
    link = '/blog/feed'
    subtitle = 'The latest blog posts from mahnamahna.net.'

    def items(self):
        index = BlogIndex.objects.get()
        return index.get_modern_posts()[:15]

    def item_title(self, item):
        if 'micro' in item.specific.tags.names():
            return get_micropost_title(item)
        else:
            return item.title

    def item_description(self, item):
        """
        Render body with 'page_id' and 'block_id' in block contexts.
        (They are required by ImageBlock and SlidesBlock.)
        """
        body = ''
        context = {'page_id': item.id}
        for block in item.specific.body:
            context['block_id'] = block.id[0:7]
            body += block.render(context)
        return body

    def item_link(self, item):
        return item.specific.get_absolute_url()
