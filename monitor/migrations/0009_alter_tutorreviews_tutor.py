# Generated by Django 5.1.6 on 2025-04-21 01:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("monitor", "0008_alter_reviews_rating"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tutorreviews",
            name="tutor",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="monitor.tutor"
            ),
        ),
    ]
