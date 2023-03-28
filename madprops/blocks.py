from wagtail.blocks import (
    CharBlock,
    ChoiceBlock,
    IntegerBlock,
    ListBlock,
    RichTextBlock,
    RawHTMLBlock,
    StreamBlock,
    StructBlock,
    StructValue,
    URLBlock,
)
from wagtail.embeds.blocks import EmbedBlock
from mnmnwag.blocks import ImageBlock, MediaBlock


class MyStreamBlock(StreamBlock):
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
            'code',
            'link',
            'image',
            'document-link',
        ],
    )
    image = ImageBlock()
    embed = EmbedBlock()
    media = MediaBlock(icon='media')
    raw_HTML = RawHTMLBlock(required=False)
    danger = RawHTMLBlock(label='DANGER!', required=False)


class InfoLinksValue(StructValue):
    def info_links_list(self):
        i = []
        links = self.get('info_links')
        for link in links:
            title = ''
            if 'voterguide' in link:
                title = 'Voter Information Guide'
            elif 'ballotpedia' in link:
                title = 'Ballotpedia'
            elif 'calmatters' in link:
                title = 'CalMatters'
            if title:
                i.append({'title': title, 'url': link})
        return i


class PropBlock(StructBlock):
    prop_number = IntegerBlock()
    prop_title = CharBlock()
    info_links = ListBlock(URLBlock)
    recommendation = ChoiceBlock(choices=[
        ('yes', 'Yes'),
        ('no', 'No'),
        ('nopos', 'No position'),
        ('noadv', 'No position (advisory measure)')
    ])
    writeup = MyStreamBlock()

    class Meta:
        icon = 'doc-full'
        template = 'madprops/blocks/prop_block.html'
        value_class = InfoLinksValue


class MadPropsStreamBlock(MyStreamBlock):
    prop = PropBlock()
