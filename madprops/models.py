from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel

from mnmnwag.models import BasePage
from .blocks import MadPropsStreamBlock


class EditionPage(BasePage):
    body = StreamField(
        MadPropsStreamBlock(),
        use_json_field=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]

    def cheat_sheet(self):
        data = []
        for block in self.body:
            if block.block_type == 'prop':
                row = {
                    'prop_number': block.value['prop_number'],
                    'prop_title': block.value['prop_title'],
                    'recommendation': block.value['recommendation'],
                }
                data.append(row)
        return data


class HomePage(BasePage):
    """
    The HomePage simply returns the latest published Edition.
    """
    max_count = 1
    template = 'madprops/edition_page.html'

    def get_context(self, request, *args, **kwargs):
        latest_edition = (
            EditionPage.objects.live()
            .public()
            .order_by('-first_published_at')
            .first()
        )
        context = latest_edition.get_context(request, *args, **kwargs)
        return context


class ArchivesPage(BasePage):
    body = StreamField(
        MadPropsStreamBlock(),
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
