from django.utils.safestring import mark_safe
from wagtail.blocks import (
    CharBlock,
    ChoiceBlock,
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


# this class is intended to be moved to the mnmnwag app
# and be imported from there
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
            'yes',
            'no',
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


class PropValues(StructValue):
    def info_links_list(self):
        i = []
        links = self.get('info_links')
        for link in links:
            title = ''
            if 'voterguide' in link or 'vigarchive' in link:
                title = 'Voter Information Guide'
            elif 'ballotpedia' in link:
                title = 'Ballotpedia'
            elif 'calmatters' in link:
                title = 'CalMatters'
            if title:
                i.append({'title': title, 'url': link})
        return i

    def rectext(self):
        rec = self.get('recommendation')
        if rec == 'yes' or rec == 'no':
            intro = 'You should vote:'
            text = rec
        elif rec == 'nopos':
            intro = mark_safe('<i>Mad Props</i> takes no position on this measure.')
            text = ''
        elif rec == 'noadv':
            intro = mark_safe('<i>Mad Props</i> takes no position on this advisory measure.')
            text = ''
        return {'intro': intro, 'text': text}


class PropBlock(StructBlock):
    prop_number = CharBlock()
    prop_title = CharBlock()
    info_links = ListBlock(URLBlock)
    recommendation = ChoiceBlock(choices=[
        ('yes', 'Yes'),
        ('no', 'No'),
        ('nopos', 'No position'),
        ('noadv', 'No position (advisory measure)')
    ])
    result = ChoiceBlock(choices=[
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], required=False)
    writeup = MyStreamBlock()

    class Meta:
        icon = 'doc-full'
        template = 'madprops/blocks/prop_block.html'
        value_class = PropValues


class MadPropsStreamBlock(MyStreamBlock):
    prop = PropBlock()
