# Generated by Django 3.1.5 on 2021-01-16 01:04

from django.db import migrations, models
import django.db.models.deletion
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0003_taggeditem_add_unique_index'),
        ('mnmnwag', '0014_auto_20201101_1744'),
    ]

    operations = [
        migrations.CreateModel(
            name='TagDescription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', wagtail.fields.RichTextField()),
                ('tag', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='taggit.tag')),
            ],
            options={
                'ordering': ['tag__name'],
            },
        ),
    ]
