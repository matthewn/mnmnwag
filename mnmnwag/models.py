from django.db import models

from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase
# from taggit.models import Tag, TaggedItemBase, GenericTaggedItemBase

from wagtail.core import blocks
from wagtail.core.models import Page
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import (
    FieldPanel,
    StreamFieldPanel
)
from wagtail.images.blocks import ImageChooserBlock
from wagtail.contrib.routable_page.models import RoutablePageMixin, route

from modelcluster.fields import ParentalKey


# ···························································
# SUPPORTING CLASSES: TAGS AND ???
# ···························································


class PostTag(TaggedItemBase):
    content_object = ParentalKey(
        Page,
        on_delete=models.CASCADE,
        related_name='tagged_items'
    )


# ···························································
# BLOG POSTS: LEGACY (FROM DRUPAL) AND MODERN (WAGTAIL)
# ···························································


class LegacyPost(Page):
    # TODO: this needs to become a plain (long) text field; we are not
    #       going to want Draftail messing with this shit
    body = RichTextField()
    tags = ClusterTaggableManager(through=PostTag, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body', classname="full"),
        FieldPanel('tags'),
    ]


class ModernPost(Page):
    body = StreamField([
        ('heading', blocks.CharBlock(classname="full title")),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('raw_HTML', blocks.RawHTMLBlock(required=False)),
    ])
    tags = ClusterTaggableManager(through=PostTag, blank=True)

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
        FieldPanel('tags'),
    ]

    subpage_types = []


# ···························································
# INDEX(ES)
# ···························································


class BlogIndex(RoutablePageMixin, Page):
    max_count = 1
    subpage_types = ['LegacyPost', 'ModernPost']

    def get_posts(self):
        return Page.objects.descendant_of(self).live().order_by('-last_published_at')

    @route(r'^$')
    def posts_all(self, request):
        self.posts = self.get_posts()
        return self.serve(request)

    @route(r'^tag/(?P<tag>[-\w]+)/$')
    def posts_by_tag(self, request, tag, *args, **kwargs):
        # self.posts = Page.objects.descendant_of(self).live().order_by('-last_published_at').filter(tags__slug=tag)
        post_tags = PostTag.objects.filter(tag__slug=tag)
        tagged_ids = [tag.content_object_id for tag in post_tags]
        self.posts = Page.objects.descendant_of(self).live().order_by('-last_published_at').filter(id__in=tagged_ids)
        return self.serve(request, *args, **kwargs)

    # add another route for posts by date
    # @route


# ···························································
# MISC PAGE(S)
# ···························································


class ComplexPage(Page):
    body = StreamField([
        ('heading', blocks.CharBlock(classname="full title")),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('raw_HTML', blocks.RawHTMLBlock(required=False)),
    ])

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
    ]

    subpage_types = []
