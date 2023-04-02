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
