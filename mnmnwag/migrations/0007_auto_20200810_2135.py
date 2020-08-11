# Generated by Django 2.2.14 on 2020-08-11 04:35

from django.db import migrations
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('mnmnwag', '0006_basicpage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='complexpage',
            name='body',
            field=wagtail.core.fields.StreamField([('heading', wagtail.core.blocks.CharBlock(classname='full title')), ('paragraph', wagtail.core.blocks.RichTextBlock()), ('image', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.core.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=False)), ('alt_text', wagtail.core.blocks.CharBlock(max_length=256, required=False))])), ('raw_HTML', wagtail.core.blocks.RawHTMLBlock(required=False))]),
        ),
        migrations.AlterField(
            model_name='modernpost',
            name='body',
            field=wagtail.core.fields.StreamField([('heading', wagtail.core.blocks.CharBlock(classname='full title')), ('paragraph', wagtail.core.blocks.RichTextBlock()), ('image', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.core.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=False)), ('alt_text', wagtail.core.blocks.CharBlock(max_length=256, required=False))])), ('raw_HTML', wagtail.core.blocks.RawHTMLBlock(required=False))]),
        ),
    ]
