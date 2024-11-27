from django.db import models
from django.forms.utils import flatatt
from django.utils.html import format_html, format_html_join

from wagtail.blocks import (
    CharBlock,
    ChoiceBlock,
    ListBlock,
    RawHTMLBlock,
    # RichTextBlock,
    StreamBlock,
    StructBlock,
    URLBlock,
)
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtailmedia.blocks import AbstractMediaChooserBlock
from wagtail_footnotes.blocks import RichTextBlockWithFootnotes as RichTextBlock


class FloatChoices(models.IntegerChoices):
    # sadly, if we store NONE as 0, Wagtail adds a '-------' item to our
    # ChoiceBlock ... so, 3 it is :(
    NONE = 3
    LEFT = 1
    RIGHT = 2


class ZoomChoices(models.IntegerChoices):
    OFF = 0
    ON = 1


class ImageBlock(StructBlock):
    image = ImageChooserBlock()
    caption = RichTextBlock(required=False, features=['bold', 'italic', 'link'])
    alt_text = CharBlock(required=False, max_length=256)
    link = URLBlock(required=False)
    float = ChoiceBlock(
        blank=False,
        choices=FloatChoices.choices,
        default=FloatChoices.NONE,
    )
    zoom = ChoiceBlock(
        choices=ZoomChoices.choices,
        default=ZoomChoices.ON,
    )

    class Meta:
        icon = 'image'
        template = 'mnmnwag/blocks/image_block.html'


class SlideBlock(StructBlock):
    image = ImageChooserBlock()
    caption = RichTextBlock(required=False, features=['bold', 'italic', 'link'])
    alt_text = CharBlock(required=False, max_length=256)


class SlidesBlock(StructBlock):
    slides = ListBlock(SlideBlock())

    class Meta:
        icon = 'image'
        template = 'mnmnwag/blocks/slides_block.html'


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


class LoadedStreamBlock(StreamBlock):
    heading = CharBlock(classname='full title')
    paragraph = RichTextBlock(
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
            'kbd'
            'code',
            'link',
            'image',
            'document-link',
        ],
    )
    image = ImageBlock()
    slides = SlidesBlock()
    embed = EmbedBlock()
    media = MediaBlock(icon='media')
    raw_HTML = RawHTMLBlock(required=False)
    danger = RawHTMLBlock(label='DANGER!', required=False)


class ModernPostStreamBlock(StreamBlock):
    heading = CharBlock(classname='full title')
    my_features = [
        'ol',
        'ul',
        'blockquote',
        'bold',
        'italic',
        'superscript',
        'subscript',
        'strikethrough',
        'kbd',
        'code',
        'footnotes',
        'link',
        'image',
        'document-link',
    ]
    teaser = RichTextBlock(features=my_features)
    paragraph = RichTextBlock(features=my_features)
    image = ImageBlock()
    slides = SlidesBlock()
    embed = EmbedBlock()
    media = MediaBlock(icon='media')
    raw_HTML = RawHTMLBlock(required=False)


class GalleryStreamBlock(StreamBlock):
    heading = CharBlock(classname='full title')
    paragraph = RichTextBlock(
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
    )
    slides = SlidesBlock()
    embed = EmbedBlock()
    media = MediaBlock(icon='media')
    raw_HTML = RawHTMLBlock(required=False)
