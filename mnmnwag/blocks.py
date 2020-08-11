from wagtail.core.blocks import (
    CharBlock,
    RichTextBlock,
    StructBlock,
)
from wagtail.images.blocks import ImageChooserBlock


class CaptionedImageBlock(StructBlock):
    image = ImageChooserBlock()
    caption = RichTextBlock(required=False, features=['bold', 'italic', 'link'])
    alt_text = CharBlock(required=False, max_length=256)

    class Meta:
        icon = 'image'
        template = 'mnmnwag/blocks/captioned_image.html'
