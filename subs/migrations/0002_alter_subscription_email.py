# Generated by Django 3.2.9 on 2021-11-06 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subs', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
