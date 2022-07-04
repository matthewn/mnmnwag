# Generated by Django 3.2.13 on 2022-07-04 23:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mnmnwag', '0030_auto_20220527_1412'),
    ]

    operations = [
        migrations.CreateModel(
            name='RejectedComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submit_date', models.DateTimeField()),
                ('name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254)),
                ('url', models.URLField(blank=True)),
                ('comment', models.TextField(max_length=3000)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('related_post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mnmnwag.modernpost')),
            ],
        ),
    ]
