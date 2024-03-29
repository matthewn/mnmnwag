# Generated by Django 4.1.7 on 2023-04-28 04:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("wagtailcore", "0083_workflowcontenttype"),
        ("mnmnwag", "0034_alter_customimage_file_alter_customrendition_file"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="rejectedcomment",
            name="related_post",
        ),
        migrations.AddField(
            model_name="rejectedcomment",
            name="related_page",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="wagtailcore.page",
            ),
            preserve_default=False,
        ),
    ]
