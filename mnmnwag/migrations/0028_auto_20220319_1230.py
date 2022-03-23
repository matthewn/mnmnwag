# Generated by Django 3.2.12 on 2022-03-19 19:30

from django.db import migrations, models
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('mnmnwag', '0027_alter_gallerypage_common_caption'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gallerypage',
            name='common_alt_text',
            field=models.CharField(blank=True, help_text='This alt text will be applied to each new slide.', max_length=256),
        ),
        migrations.AlterField(
            model_name='gallerypage',
            name='common_caption',
            field=wagtail.core.fields.RichTextField(blank=True, help_text='This caption will be applied to each new slide.'),
        ),
    ]