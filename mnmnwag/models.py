from django.core.paginator import Paginator
from django.db import models

from modelcluster.fields import ParentalKey
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

from django_comments.moderation import CommentModerator
from django_comments_xtd.moderation import moderator

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


class BlogPost(models.Model):
    def get_absolute_url(self):
        """
        Returns an absolute URL for the page.
        (Required by django_comments_xtd.)
        """
        return self.full_url

    def page_message(self):
        return self.get_parent().specific.page_message

    class Meta:
        abstract = True


class LegacyPost(Page, BlogPost):
    # TODO: this needs to become a plain (long) text field; we are not
    #       going to want Draftail messing with this shit
    body = RichTextField()
    tags = ClusterTaggableManager(through=PostTag, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body', classname="full"),
        FieldPanel('tags'),
    ]

    subpage_types = []


class ModernPost(Page, BlogPost):
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
    page_message = RichTextField()
    max_count = 1
    subpage_types = ['LegacyPost', 'ModernPost']

    content_panels = Page.content_panels + [
        FieldPanel('page_message'),
    ]

    def get_posts(self):
        return Page.objects.descendant_of(self).live().order_by('-last_published_at')

    def paginate_posts(self, request, posts):
        paginator = self.truncate_paginator(Paginator(posts, 4))
        page_number = request.GET.get('page')
        return paginator.get_page(page_number)

    def truncate_paginator(self, paginator):
        """
        Provide a truncated (if necessary) page list by adding a
        display_range property to the provided paginator.
        """
        if len(paginator.page_range) > 10:
            display_range = [1, 2]
            display_range += ['...']

            start = 2
            end = paginator.num_pages - 1
            length = 7
            display_range += [start + x * (end - start) // (length - 1) for x in range(length)][1:-1]

            display_range += ['...']
            display_range += [paginator.num_pages - 1, paginator.num_pages]
        else:
            display_range = paginator.page_range
        paginator.display_range = display_range
        return paginator

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
    page_message = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel('page_message'),
        StreamFieldPanel('body'),
    ]


# ···························································
# COMMENT MODERATOR CLASS & REGISTRATION
# ···························································

class BlogPostModerator(CommentModerator):
    email_notification = True

    def moderate(self, comment, content_object, request):
        # moderate all messages
        if request.user.is_superuser:
            return False
        else:
            return True


moderator.register(LegacyPost, BlogPostModerator)
moderator.register(ModernPost, BlogPostModerator)
