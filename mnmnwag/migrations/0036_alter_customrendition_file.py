# Generated by Django 4.2.1 on 2023-05-11 04:41

from django.db import migrations
import wagtail.images.models


class Migration(migrations.Migration):

    dependencies = [
        ("mnmnwag", "0035_remove_rejectedcomment_related_post_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customrendition",
            name="file",
            field=wagtail.images.models.WagtailImageField(
                height_field="height",
                storage=wagtail.images.models.get_rendition_storage,
                upload_to=wagtail.images.models.get_rendition_upload_to,
                width_field="width",
            ),
        ),
    ]
