# Generated by Django 4.2.18 on 2025-01-31 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("demo", "0002_superorg_demo_super_org"),
    ]

    operations = [
        migrations.AddField(
            model_name="demo",
            name="name_formats",
            field=models.JSONField(blank=True, null=True),
        ),
    ]
