from django.core.paginator import Paginator
from django.db import models

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

from wagtail.admin.edit_handlers import (
    FieldPanel,
    StreamFieldPanel,
)
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.models import Image, AbstractImage, AbstractRendition
from wagtail.search import index

from wagtailmedia.models import Media, AbstractMedia

from django_comments.moderation import CommentModerator
from django_comments_xtd.moderation import moderator

from .blocks import CaptionedImageBlock, MediaBlock

import datetime as dt


# ···························································
# CUSTOM BASE PAGE MODEL AND MISC PAGE(S)
# ···························································


class BasePage(Page):
    def get_context(self, request):
        context = super().get_context(request)
        try:
            context['theme_class'] = request.COOKIES['themeClass']
        except KeyError:
            context['theme_class'] = 'theme-light'
        return context

    class Meta:
        abstract = True


class ComplexPage(BasePage):
    body = StreamField([
        ('heading', blocks.CharBlock(classname="full title")),
        ('paragraph', blocks.RichTextBlock()),
        ('image', CaptionedImageBlock()),
        ('embed', EmbedBlock()),
        ('media', MediaBlock(icon='media')),
        ('raw_HTML', blocks.RawHTMLBlock(required=False)),
    ])
    page_message = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel('page_message'),
        StreamFieldPanel('body'),
    ]


class BasicPage(BasePage):
    body = RichTextField(
        blank=True,
        features=['bold', 'italic', 'h3', 'h4', 'h5', 'blockquote', 'ol', 'ul', 'link', 'image', 'document-link'],
    )

    content_panels = Page.content_panels + [
        FieldPanel('body', classname='full'),
    ]


# ···························································
# SUPPORTING CLASSES: TAGS AND SIDEBAR ELEMENTS
# ···························································


class PostTag(TaggedItemBase):
    content_object = ParentalKey(
        Page,
        on_delete=models.CASCADE,
        related_name='tagged_items'
    )


class BlogSidebar():
    def archives_by_tag(self):
        top = ['life', 'micro', 'site', 'snapshot', 'tech']
        post_tags = PostTag.tags_for(Page).order_by('name')
        bottom_tags = []
        top_tags = []
        for tag in post_tags:
            if tag.name in top:
                top_tags.append(tag)
            else:
                bottom_tags.append(tag)
        content = '<ul>'
        for tag in top_tags:
            content += self.get_tag_link_li(tag)
        content += '</ul><ul>'
        for tag in bottom_tags:
            content += self.get_tag_link_li(tag)
        content += '</ul>'
        return content

    def archives_by_year(self):
        # TODO/FIXME: the way the years list gets built is stupid;
        # we should just fetch distinct years from post dates
        years = list(range(2003, 2011))
        this_year = dt.date.today().year
        years += list(range(2020, this_year + 1))
        content = '<ul>'
        for year in years:
            start_date = dt.datetime(year, 1, 1)
            end_date = dt.datetime(year + 1, 1, 1)
            count = (
                Page.objects.filter(first_published_at__gte=start_date)
                .filter(first_published_at__lt=end_date)
                .count()
            )
            if count:
                idx = self.get_idx_obj()
                href = idx.url + idx.reverse_subpage('posts_by_date', kwargs={'year': year})
                # ideally this would be in a template somewhere
                content += f'<li><a href="{href}" up-target="#header, #content .blog" up-transition="cross-fade">{year}</a> ({count})</li>'
        content += '</ul>'
        return content

    def blogroll(self):
        page = BasicPage.objects.get(title='Blogroll')
        return page.body

    def get_tag_link_li(self, tag):
        count = PostTag.objects.filter(tag=tag).count()
        idx = self.get_idx_obj()
        href = idx.url + idx.reverse_subpage('posts_by_tag', kwargs={'tag': tag})
        # ideally this would be in a template somewhere
        content = f'<li><a href="{href}" up-target="#header, #content .blog" up-transition="cross-fade">#{tag}</a> ({count})</li>'
        return content

    def get_idx_obj(self):
        return BlogIndex.objects.get()


# ···························································
# BLOG POSTS: LEGACY (FROM DRUPAL) AND MODERN (WAGTAIL)
# ···························································


class BlogPost(models.Model, BlogSidebar):
    has_comments_enabled = models.BooleanField(
        default=True,
        verbose_name='Comments enabled',
    )
    tags = ClusterTaggableManager(through=PostTag, blank=True)

    search_fields = Page.search_fields + [
        index.SearchField('title'),
        index.SearchField('body'),
    ]

    def get_absolute_url(self):
        """
        Returns an absolute URL for the page. (Required by django_comments_xtd.)
        """
        return self.full_url

    def page_message(self):
        return self.get_parent().specific.page_message

    class Meta:
        abstract = True


class LegacyPost(BasePage, BlogPost):
    # TODO: this needs to become a plain (long) text field; we are not
    #       going to want Draftail messing with this shit
    body = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel('body', classname="full"),
        FieldPanel('tags'),
        FieldPanel('has_comments_enabled'),
    ]

    subpage_types = []


class ModernPost(BasePage, BlogPost):
    body = StreamField([
        ('heading', blocks.CharBlock(classname="full title")),
        ('paragraph', blocks.RichTextBlock()),
        ('image', CaptionedImageBlock()),
        ('embed', EmbedBlock()),
        ('media', MediaBlock(icon='media')),
        ('raw_HTML', blocks.RawHTMLBlock(required=False)),
    ])

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
        FieldPanel('tags'),
        FieldPanel('has_comments_enabled'),
    ]

    subpage_types = []

    def full_clean(self, *args, **kwargs):
        """ Override method in order to provide default slug for micro posts """
        if self.is_micro():
            base_slug = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%MZ')
            self.slug = self._get_autogenerated_slug(base_slug)
        super(ModernPost, self).full_clean(*args, **kwargs)

    def is_micro(self):
        return True if 'micro' in self.tags.names() else False

    def is_snapshot(self):
        return True if 'snapshot' in self.tags.names() else False


# ···························································
# INDEX(ES)
# ···························································


class BlogIndex(RoutablePageMixin, BasePage, BlogSidebar):
    page_message = RichTextField()
    max_count = 1
    subpage_types = ['LegacyPost', 'ModernPost']

    content_panels = Page.content_panels + [
        FieldPanel('page_message'),
    ]

    def get_posts(self):
        return Page.objects.descendant_of(self).live().order_by('-first_published_at')

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
            self.get_posts().filter(first_published_at__gte=start_date).filter(first_published_at__lt=end_date),
        )
        return self.serve(request, *args, **kwargs)

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


# ···························································
# COMMENT MODERATOR CLASS & REGISTRATION
# ···························································

class BlogPostModerator(CommentModerator):
    email_notification = True
    enable_field = 'has_comments_enabled'

    def moderate(self, comment, content_object, request):
        # moderate all messages unless superuser is posting
        if request.user.is_superuser:
            return False
        else:
            return True


moderator.register(LegacyPost, BlogPostModerator)
moderator.register(ModernPost, BlogPostModerator)


# ···························································
# CUSTOM MEDIA CLASSES                       (for future use)
# ···························································

class CustomImage(AbstractImage):
    # Add any extra fields to image here

    # eg. To add a caption field:
    # caption = models.CharField(max_length=255, blank=True)

    admin_form_fields = Image.admin_form_fields + (
        # Then add the field names here to make them appear in the form:
        # 'caption',
    )


class CustomRendition(AbstractRendition):
    image = models.ForeignKey(CustomImage, on_delete=models.CASCADE, related_name='renditions')

    class Meta:
        unique_together = (
            ('image', 'filter_spec', 'focal_point_key'),
        )


class CustomMedia(AbstractMedia):
    # Add any extra fields to image here

    # eg. To add a caption field:
    # caption = models.CharField(max_length=255, blank=True)

    admin_form_fields = Media.admin_form_fields + (
        # Then add the field names here to make them appear in the form:
        # 'caption',
    )
