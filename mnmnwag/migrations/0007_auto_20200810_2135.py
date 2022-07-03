# Generated by Django 2.2.14 on 2020-08-11 04:35

from django.db import migrations
import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('mnmnwag', '0006_basicpage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='complexpage',
            name='body',
            field=wagtail.fields.StreamField([('heading', wagtail.blocks.CharBlock(classname='full title')), ('paragraph', wagtail.blocks.RichTextBlock()), ('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=False)), ('alt_text', wagtail.blocks.CharBlock(max_length=256, required=False))])), ('raw_HTML', wagtail.blocks.RawHTMLBlock(required=False))]),
        ),
        migrations.AlterField(
            model_name='modernpost',
            name='body',
            field=wagtail.fields.StreamField([('heading', wagtail.blocks.CharBlock(classname='full title')), ('paragraph', wagtail.blocks.RichTextBlock()), ('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=False)), ('alt_text', wagtail.blocks.CharBlock(max_length=256, required=False))])), ('raw_HTML', wagtail.blocks.RawHTMLBlock(required=False))]),
        ),
    ]
