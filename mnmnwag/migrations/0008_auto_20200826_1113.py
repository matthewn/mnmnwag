# Generated by Django 2.2.15 on 2020-08-26 18:13

from django.db import migrations
import wagtail.blocks
import wagtail.fields
import wagtail.embeds.blocks
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('mnmnwag', '0007_auto_20200810_2135'),
    ]

    operations = [
        migrations.AlterField(
            model_name='modernpost',
            name='body',
            field=wagtail.fields.StreamField([('heading', wagtail.blocks.CharBlock(classname='full title')), ('paragraph', wagtail.blocks.RichTextBlock()), ('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=False)), ('alt_text', wagtail.blocks.CharBlock(max_length=256, required=False))])), ('embed', wagtail.embeds.blocks.EmbedBlock()), ('raw_HTML', wagtail.blocks.RawHTMLBlock(required=False))]),
        ),
    ]
