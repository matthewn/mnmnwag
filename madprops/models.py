from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel

from mnmnwag.models import BasePage
from .blocks import MadPropsStreamBlock


class EditionPage(BasePage):
    body = StreamField(
        MadPropsStreamBlock(),
        use_json_field=True
    )

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]
