from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db import models
from django.template import loader
from django.utils import timezone

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import Tag, TaggedItemBase

from wagtail.admin.edit_handlers import (
    FieldPanel,
    MultiFieldPanel,
    StreamFieldPanel,
)
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page
from wagtail.core.models.collections import Collection
from wagtail.core.rich_text import RichText
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images import get_image_model
from wagtail.images.models import Image, AbstractImage, AbstractRendition
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from wagtailmedia.models import Media, AbstractMedia

from django_comments.moderation import CommentModerator
from django_comments_xtd.moderation import moderator

from honeypot.decorators import honeypot_equals

from .blocks import ImageBlock, MediaBlock, SlidesBlock
from .utils import get_elided_page_range

import datetime as dt
import pyexiv2
import re


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
        ('paragraph', blocks.RichTextBlock(
            features=[
                'ol',
                'ul',
                'blockquote',
                'bold',
                'italic',
                'superscript',
                'subscript',
                'strikethrough',
                'code',
                'link',
                'image',
                'document-link',
            ],
        )),
        ('image', ImageBlock()),
        ('slides', SlidesBlock()),
        ('embed', EmbedBlock()),
        ('media', MediaBlock(icon='media')),
        ('raw_HTML', blocks.RawHTMLBlock(required=False)),
        ('danger', blocks.RawHTMLBlock(label='DANGER!', required=False)),
    ])
    page_message = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel('page_message'),
        StreamFieldPanel('body'),
    ]


class BasicPage(BasePage):
    body = RichTextField(
        blank=True,
        features=[
            'h3',
            'h4',
            'h5',
            'ol',
            'ul',
            'blockquote',
            'bold',
            'italic',
            'superscript',
            'subscript',
            'strikethrough',
            'code',
            'link',
            'image',
            'document-link',
        ],
    )

    content_panels = Page.content_panels + [
        FieldPanel('body', classname='full'),
    ]


class GalleryPage(BasePage):
    body = StreamField([
        ('heading', blocks.CharBlock(classname="full title")),
        ('paragraph', blocks.RichTextBlock(
            features=[
                'blockquote',
                'bold',
                'italic',
                'superscript',
                'subscript',
                'strikethrough',
                'link',
                'image',
                'document-link',
            ],
        )),
        ('slides', SlidesBlock()),
        ('embed', EmbedBlock()),
        ('media', MediaBlock(icon='media')),
        ('raw_HTML', blocks.RawHTMLBlock(required=False)),
    ])

    # fields for the create-from-collection functionality
    import_collection = models.ForeignKey(
        Collection,
        blank=True,
        on_delete=models.SET_NULL,
        null=True,
    )
    common_alt_text = models.CharField(
        blank=True,
        help_text='This alt text will be applied to each new slide.',
        max_length=256,
    )
    common_caption = RichTextField(
        blank=True,
        help_text='This caption will be applied to each new slide.',
        features=['bold', 'italic', 'link'],
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('import_collection'),
                FieldPanel('common_alt_text'),
                FieldPanel('common_caption'),
            ],
            heading='Create Slides from a Collection',
            classname='collapsible collapsed',
            help_text='Slides will be created in this page\'s Body when you Save.',
        ),
        StreamFieldPanel('body'),
    ]

    def get_exif_description(self, image):
        """
        Return an image's EXIF ImageDescription or None.
        """
        f = image.file.file.open()
        i = pyexiv2.ImageData(f.read())
        exif_desc = i.read_exif().get('Exif.Image.ImageDescription')
        i.close()
        return exif_desc

    def save_revision(self, **kwargs):
        """
        If an import_collection is provided, append its images to the body in a
        SlidesBlock. Include common_alt_text and common_caption in each slide
        if provided. Clear these three fields before moving on.
        """
        if self.import_collection:

            i = get_image_model()
            images = i.objects.filter(collection=self.import_collection).order_by('file')

            slides_block = []
            for image in images:
                # check for EXIF ImageDescription, prefer over common_caption
                exif_desc = self.get_exif_description(image)
                caption = exif_desc or self.common_caption
                slide_block = {
                    'image': image,
                    'caption': RichText(caption),
                    'alt_text': self.common_alt_text,
                }
                slides_block.append(slide_block)
            self.body.append(('slides', {'slides': slides_block}))

            self.import_collection = None
            self.common_alt_text = ''
            self.common_caption = ''

        return super(GalleryPage, self).save_revision(**kwargs)


# ···························································
# SUPPORTING CLASSES: TAGS AND SIDEBAR ELEMENTS
# ···························································


class PostTag(TaggedItemBase):
    content_object = ParentalKey(
        Page,
        on_delete=models.CASCADE,
        related_name='tagged_items',
    )


@register_snippet
class TagDescription(models.Model):
    tag = models.OneToOneField(
        Tag,
        on_delete=models.CASCADE,
    )
    description = RichTextField(
        features=[
            'bold',
            'italic',
            'superscript',
            'subscript',
            'strikethrough',
            'code',
            'link',
        ],
    )

    panels = [
        FieldPanel('tag'),
        FieldPanel('description'),
    ]

    def __str__(self):
        return self.tag.name

    class Meta:
        ordering = ['tag__name']


class BlogSidebar():
    def archives_by_tag(self):
        top = ['micro', 'snapshot']
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
        idx = self.get_idx_obj()
        years = [d.year for d in Page.objects.dates('first_published_at', 'year')]
        years.reverse()
        content = '<ul>'
        for year in years:
            start_date = dt.datetime(year, 1, 1)
            end_date = dt.datetime(year + 1, 1, 1)
            count = (
                Page.objects.descendant_of(idx)
                .filter(first_published_at__gte=start_date)
                .filter(first_published_at__lt=end_date)
                .count()
            )
            if count:
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
        # NOTE! This code assumes there will only ever be one BlogIndex page.
        # (there must be a better way to do this...)
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
    body = models.TextField()
    old_path = models.CharField(max_length=64)

    content_panels = Page.content_panels + [
        FieldPanel('old_path'),
        FieldPanel('body', classname='full'),
        FieldPanel('tags'),
        FieldPanel('has_comments_enabled'),
    ]

    settings_panels = Page.settings_panels + [
        FieldPanel('first_published_at'),
    ]

    search_fields = Page.search_fields + [
        index.SearchField('title'),
        index.SearchField('body'),
    ]

    subpage_types = []


class ModernPost(BasePage, BlogPost):
    body = StreamField([
        ('heading', blocks.CharBlock(classname='full title')),
        ('teaser', blocks.RichTextBlock(
            features=[
                'ol',
                'ul',
                'blockquote',
                'bold',
                'italic',
                'superscript',
                'subscript',
                'strikethrough',
                'code',
                'link',
                'image',
                'document-link',
            ],
        )),
        ('paragraph', blocks.RichTextBlock(
            features=[
                'ol',
                'ul',
                'blockquote',
                'bold',
                'italic',
                'superscript',
                'subscript',
                'strikethrough',
                'code',
                'link',
                'image',
                'document-link',
            ],
        )),
        ('image', ImageBlock()),
        ('slides', SlidesBlock()),
        ('embed', EmbedBlock()),
        ('media', MediaBlock(icon='media')),
        ('raw_HTML', blocks.RawHTMLBlock(required=False)),
    ])

    tweet_title = models.TextField(
        blank=True,
        max_length=256,
    )

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
        FieldPanel('tags'),
        FieldPanel('has_comments_enabled'),
    ]

    promote_panels = [FieldPanel('tweet_title')] + Page.promote_panels

    search_fields = Page.search_fields + [
        index.SearchField('title'),
        index.SearchField('body'),
    ]

    subpage_types = []

    def full_clean(self, *args, **kwargs):
        """ Override method to provide default slug for micro posts. """
        if self.is_micro() and not self.url:
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
    subpage_types = ['ModernPost']

    content_panels = Page.content_panels + [
        FieldPanel('page_message'),
    ]

    def get_posts(self):
        return Page.objects.descendant_of(self).live().order_by('-first_published_at')

    def get_modern_posts(self):
        return ModernPost.objects.descendant_of(self).live().order_by('-first_published_at')

    def paginate_posts(self, request, posts):
        paginator = Paginator(posts, 20)
        page_number = request.GET.get('page')
        display_range = get_elided_page_range(
            num_pages=paginator.num_pages,
            page_range=paginator.page_range,
            number=page_number,
        )
        paginator.display_range = display_range
        return paginator.get_page(page_number)

    @route(r'^$')
    def posts_main(self, request):
        """
        This is the "main" blog index route, which lives at /blog.
        Only show ModernPosts here so that the pager is not dominated by
        ancient stuff. LegacyPosts are available in the other routes.
        """
        self.posts = self.paginate_posts(request, self.get_modern_posts())
        return self.serve(request)

    @route(r'^(?P<year>20\d\d)\/?(?P<month>[0-1][0-9])?\/?(?P<day>[0-3][0-9])?/$')
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
        post_tags = PostTag.objects.filter(tag__slug=tag.lower())
        post_ids = [item.content_object_id for item in post_tags]
        self.posts = self.paginate_posts(
            request,
            self.get_posts().filter(id__in=post_ids),
        )
        self.index_title = f'Posts tagged #{tag}'
        try:
            self.tag_description = TagDescription.objects.get(tag__slug=tag.lower()).description
        except TagDescription.DoesNotExist:
            pass
        return self.serve(request, *args, **kwargs)


# ···························································
# COMMENT MODERATOR CLASS & REGISTRATION
# (TODO: need a better place for this to live)
# ···························································

class BlogPostModerator(CommentModerator):
    email_notification = True
    enable_field = 'has_comments_enabled'

    def allow(self, comment, content_object, request):
        """
        Override parent method to include django-honeypot in the mix,
        and to add a few custom anti-spam rules of our own.
        """
        # here to END_OF_DIFFS = our additions to this method

        if not self.verify_honeypot(request):
            return False

        # disallow any comment with Cyrillic characters in it
        # (Russian spam-bots are the absolute worst!)
        if bool(re.search('[а-яА-Я]', comment.comment)):
            return False

        # disallow common pattern as of Feb. 2022:
        #   email ending in .ru with a link in the comment
        # (Russian spam-bots are the absolute worst!)
        if (
            bool(re.search(r'\.ru$', comment.user_email))
            and 'http' in comment.comment
        ):
            return False

        # disallow common pattern as of Mar. 2022:
        #   multiple .ru links in comment body
        # (Russian spam-bots are the absolute worst!)
        if len(re.findall(r'https?:\/\/.*?\.ru', comment.comment)) > 2:
            return False

        # END_OF_DIFFS

        if self.enable_field:
            if not getattr(content_object, self.enable_field):
                return False
        if self.auto_close_field and self.close_after is not None:
            close_after_date = getattr(content_object, self.auto_close_field)
            if close_after_date is not None and self._get_delta(timezone.now(),
                                                                close_after_date).days >= self.close_after:
                return False
        return True

    def email(self, comment, content_object, request):
        """
        Override parent method to inject request into notification template
        context.
        """
        if not self.email_notification:
            return
        recipient_list = [manager_tuple[1] for manager_tuple in settings.MANAGERS]
        t = loader.get_template('comments/comment_notification_email.txt')
        c = {
            'comment': comment,
            'content_object': content_object,
            'request': request,  # this line is our only alteration to this method
        }
        subject = ('[%(site)s] New comment posted on "%(object)s"') % {
            'site': get_current_site(request).name,
            'object': content_object,
        }
        message = t.render(c)
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=True)

    def moderate(self, comment, content_object, request):
        """
        Override parent method. Moderate all messages unless superuser is
        posting.
        """
        if request.user.is_superuser:
            return False
        else:
            return True

    def verify_honeypot(self, request, field_name=None):
        """
        Modded version of honeypot.validators.verify_honeypot_value().
        Returns True or False; to be used in allow() in this class.
        """
        verifier = getattr(settings, "HONEYPOT_VERIFIER", honeypot_equals)
        if request.method == "POST":
            field = field_name or settings.HONEYPOT_FIELD_NAME
            if field not in request.POST or not verifier(request.POST[field]):
                return False
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


# ···························································
# SINGLETON ABSTRACT CLASS & ITS CHILDREN
# ···························································

class SingletonModel(models.Model):
    """
    Defines a model with only one row. Taken from:
    https://steelkiwi.com/blog/practical-application-singleton-design-pattern/
    """
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class TweetsTracker(SingletonModel):
    last_run_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Tweets job tracker'
