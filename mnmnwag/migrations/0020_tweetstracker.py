# Generated by Django 3.2.9 on 2021-11-11 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mnmnwag', '0019_auto_20211103_1023'),
    ]

    operations = [
        migrations.CreateModel(
            name='TweetsTracker',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_run_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Tweets job tracker',
            },
        ),
    ]
