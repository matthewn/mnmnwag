from django.db import models

from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel

from django_comments_xtd.moderation import moderator

from mnmnwag.models import BasePage, BlogPostModerator
from .blocks import MadPropsStreamBlock


class SimplePage(BasePage):
    body = StreamField(
        MadPropsStreamBlock(),
        use_json_field=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]


class EditionPage(BasePage):
    body = StreamField(
        MadPropsStreamBlock(),
        use_json_field=True,
    )
    has_comments_enabled = models.BooleanField(
        default=True,
        verbose_name='Comments enabled',
    )

    content_panels = Page.content_panels + [
        FieldPanel('body'),
        FieldPanel('has_comments_enabled'),
        FieldPanel('first_published_at'),
    ]

    def cheat_sheet(self):
        return [
            {
                'prop_number': block.value['prop_number'],
                'prop_title': block.value['prop_title'],
                'recommendation': block.value['recommendation'],
            }
            for block in self.body if block.block_type == 'prop'
        ]

    def get_absolute_url(self):
        """
        Returns an absolute URL for the page. (Required by django_comments_xtd.)
        """
        return self.full_url


class HomePage(BasePage):
    """
    The HomePage simply returns the latest published Edition.
    """
    max_count = 1
    subpage_types = [SimplePage, EditionPage]
    template = 'madprops/edition_page.html'

    def get_context(self, request, *args, **kwargs):
        latest_edition = (
            EditionPage.objects.live()
            .public()
            .order_by('-first_published_at')
            .first()
        )
        context = latest_edition.get_context(request, *args, **kwargs)
        context['theres_no_place_like_home'] = True
        return context


class ArchivesPage(BasePage):
    body = StreamField(
        MadPropsStreamBlock(),
        blank=True,
        use_json_field=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]

    max_count = 1

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context['editions'] = (
            EditionPage.objects.live()
            .public()
            .order_by('-first_published_at')[1:]
        )
        return context


class EditionModerator(BlogPostModerator):
    pass


moderator.register(EditionPage, EditionModerator)