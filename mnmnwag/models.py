from django.core.paginator import Paginator
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
from wagtail.contrib.routable_page.models import RoutablePageMixin, route

from modelcluster.fields import ParentalKey

import datetime as dt


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

    def paginate_posts(self, request, posts):
        paginator = Paginator(posts, 2)
        page_number = request.GET.get('page') if request.GET.get('page') else 1
        return paginator.get_page(page_number)

    @route(r'^$')
    def posts_all(self, request):
        self.posts = self.paginate_posts(request, self.get_posts())
        return self.serve(request)

    @route(r'^tag/(?P<tag>[-\w]+)/$')
    def posts_by_tag(self, request, tag, *args, **kwargs):
        post_tags = PostTag.objects.filter(tag__slug=tag)
        tagged_ids = [tag.content_object_id for tag in post_tags]
        self.posts = self.paginate_posts(
            request,
            self.get_posts().filter(id__in=tagged_ids),
        )
        self.index_title = f'Posts tagged #{tag}'
        return self.serve(request, *args, **kwargs)

    @route(r'(?P<year>20\d\d)\/?(?P<month>[0-1][0-9])?\/?(?P<day>[0-3][0-9])?/$')
    def posts_by_date(self, request, year, month='', day='', *args, **kwargs):
        if day:
            start_date = dt.datetime(int(year), int(month), int(day))
            display_day = int(day)
            display_month = start_date.strftime("%B")
            end_date = start_date + dt.timedelta(days=1)
            self.index_title = f'Posts from {display_day} {display_month} {year}'
        elif month:
            start_date = dt.datetime(int(year), int(month), 1)
            start_month = start_date.month
            display_month = start_date.strftime("%B")
            start_year = start_date.year
            end_month = 1 if start_date.month == 12 else start_month + 1
            end_year = start_year + 1 if start_date.month == 12 else start_year
            end_date = dt.datetime(end_year, end_month, 1)
            self.index_title = f'Posts from {display_month} {start_year}'
        else:
            start_date = dt.datetime(int(year), 1, 1)
            end_date = dt.datetime(int(year) + 1, 1, 1)
            self.index_title = f'Posts from {year}'
        self.posts = self.paginate_posts(
            request,
            self.get_posts().filter(first_published_at__gt=start_date).filter(first_published_at__lt=end_date),
        )
        return self.serve(request, *args, **kwargs)


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
