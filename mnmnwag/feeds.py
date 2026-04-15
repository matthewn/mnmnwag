from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from taggit.models import Tag
from .models import BlogIndex, PostTag


class LatestEntriesFeed(Feed):
    feed_type = Atom1Feed
    title = 'mahnamahna.net/blog'
    author_name = r'/\/\/\/'

    def link(self, obj):
        link = '/blog/feed'
        if obj:
            link += ','.join([str(t.id) for t in obj])
        return link

    def subtitle(self, obj):
        subtitle = 'The latest blog posts from mahnamahna.net.'
        if obj:
            subtitle = subtitle[0:-1] + ' tagged as: '
            subtitle += ', '.join([t.name for t in obj])
        return subtitle

    def get_object(self, request, tag_ids=None):
        """
        Allow for filtering by tags.
        tag_ids is a string of comma-separated numbers
        """
        tags = []
        if tag_ids:
            tag_ids_list = [
                item for item in tag_ids.split(',') if item.isdigit()
            ]
            if tag_ids_list:
                tags = Tag.objects.filter(id__in=tag_ids_list)
        return tags

    def items(self, obj):
        index = BlogIndex.objects.get()
        posts = index.get_modern_posts()
        if obj:
            # mimics logic in BlogIndex.posts_by_tag()
            post_tags = PostTag.objects.filter(tag__id__in=obj)
            post_ids = [item.content_object_id for item in post_tags]
            posts = posts.filter(id__in=post_ids)
        return posts[:15]

    def item_title(self, item):
        if 'micro' in item.specific.tags.names():
            return item.specific.micropost_title
        else:
            return item.title

    def item_author_name(self):
        return self.author_name

    def item_description(self, item):
        """
        Render body with 'page_id', 'block_id', and 'page' in block contexts.
        page_id and block_id are required by ImageBlock and SlidesBlock;
        page is required by RichTextBlockWithFootnotes to resolve footnote tags.
        """
        from django.template.loader import get_template

        page = item.specific
        body = ''
        context = {'page_id': page.id, 'page': page}
        for block in page.body:
            context['block_id'] = block.id[0:7]
            body += block.render(context)

        if getattr(page, 'footnotes_list', None):
            template = get_template('wagtail_footnotes/includes/footnotes.html')
            body += template.render({'page': page})

        return body

    def item_link(self, item):
        return item.specific.get_absolute_url()

    def item_updateddate(self, item):
        return item.specific.first_published_at
