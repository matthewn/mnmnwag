# Generated by Django 5.1.6 on 2025-02-14 01:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mnmnwag", "0041_rename_tweetstracker_tootstracker_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="modernpost",
            name="do_not_tweet",
        ),
        migrations.RemoveField(
            model_name="modernpost",
            name="tweet_title",
        ),
        migrations.AddField(
            model_name="modernpost",
            name="toot_text",
            field=models.TextField(blank=True, max_length=477),
        ),
        migrations.AddField(
            model_name="modernpost",
            name="toot_this",
            field=models.BooleanField(
                default=False,
                help_text="Automatically generate a tweet about this post.",
                verbose_name="Toot this",
            ),
        ),
    ]
