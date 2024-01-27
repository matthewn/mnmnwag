# Generated by Django 5.0.1 on 2024-01-27 05:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("mnmnwag", "0036_alter_customrendition_file"),
    ]

    operations = [
        migrations.CreateModel(
            name="FeedsIndex",
            fields=[
                (
                    "complexpage_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="mnmnwag.complexpage",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("mnmnwag.complexpage",),
        ),
    ]