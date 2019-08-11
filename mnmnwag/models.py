from django.db import models

from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

from wagtail.core import blocks
from wagtail.core.models import Page
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import (
    FieldPanel,
    StreamFieldPanel
)
from wagtail.images.blocks import ImageChooserBlock

from modelcluster.fields import ParentalKey


# ···························································
# SUPPORTING CLASSES: TAGS AND ???
# ···························································


class LegacyPostTag(TaggedItemBase):
    content_object = ParentalKey(
        'LegacyPost',
        on_delete=models.CASCADE,
        related_name='tagged_items'
    )


class ModernPostTag(TaggedItemBase):
    content_object = ParentalKey(
        'ModernPost',
        on_delete=models.CASCADE,
        related_name='tagged_items'
    )


# ···························································
# BLOG POSTS: LEGACY (FROM DRUPAL) AND MODERN (WAGTAIL)
# ···························································


class LegacyPost(Page):
    body = RichTextField()
    tags = ClusterTaggableManager(through=LegacyPostTag, blank=True)

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

    tags = ClusterTaggableManager(through=ModernPostTag, blank=True)

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
        FieldPanel('tags'),
    ]

    subpage_types = []


# ···························································
# INDEX(ES)
# ···························································


class BlogIndex(Page):
    max_count = 1
    subpage_types = ['LegacyPost', 'ModernPost']

    def posts(self):
        posts = self.get_children().specific().live().order_by('-last_published_at')
        return posts


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
