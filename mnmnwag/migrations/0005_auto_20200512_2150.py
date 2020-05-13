# Generated by Django 2.2.12 on 2020-05-13 04:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mnmnwag', '0004_auto_20200426_0118'),
    ]

    operations = [
        migrations.AddField(
            model_name='legacypost',
            name='has_comments_enabled',
            field=models.BooleanField(default=True, verbose_name='Comments enabled'),
        ),
        migrations.AddField(
            model_name='modernpost',
            name='has_comments_enabled',
            field=models.BooleanField(default=True, verbose_name='Comments enabled'),
        ),
    ]
