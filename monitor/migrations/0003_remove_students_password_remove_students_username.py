# Generated by Django 4.2.18 on 2025-03-05 06:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("monitor", "0002_students_classes"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="students",
            name="password",
        ),
        migrations.RemoveField(
            model_name="students",
            name="username",
        ),
    ]
