# Generated by Django 3.2.9 on 2021-11-06 22:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subs', '0002_alter_subscription_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubscriptionsTracker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_run_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Subscriptions job tracker',
            },
        ),
    ]
