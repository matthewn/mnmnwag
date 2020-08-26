from django.forms.utils import flatatt
from django.utils.html import format_html, format_html_join

from wagtail.core.blocks import (
    CharBlock,
    RichTextBlock,
    StructBlock,
)
from wagtail.images.blocks import ImageChooserBlock
from wagtailmedia.blocks import AbstractMediaChooserBlock


class CaptionedImageBlock(StructBlock):
    image = ImageChooserBlock()
    caption = RichTextBlock(required=False, features=['bold', 'italic', 'link'])
    alt_text = CharBlock(required=False, max_length=256)

    class Meta:
        icon = 'image'
        template = 'mnmnwag/blocks/captioned_image.html'


class MediaBlock(AbstractMediaChooserBlock):
    def render_basic(self, value, context=None):
        if not value:
            return ''

        if value.type == 'video':
            player_code = '''
            <div>
                <video width="320" height="240" controls>
                    {0}
                    Your browser does not support the video tag.
                </video>
            </div>
            '''
        else:
            player_code = '''
            <div>
                <audio controls>
                    {0}
                    Your browser does not support the audio element.
                </audio>
            </div>
            '''

        return format_html(player_code, format_html_join(
            '\n', "<source{0}>",
            [[flatatt(s)] for s in value.sources]
        ))
