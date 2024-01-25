# Generated by Django 3.2.23 on 2024-01-25 12:57

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Todo",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        help_text="Title of todo.",
                        max_length=100,
                        verbose_name="Title",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="Description of todo.",
                        verbose_name="Description",
                    ),
                ),
                (
                    "completed",
                    models.BooleanField(
                        default=False,
                        help_text="Is todo completed?",
                        verbose_name="Completed",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="When instance created.",
                        verbose_name="Created",
                    ),
                ),
                (
                    "last_modified",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="When instance modified recently.",
                        verbose_name="Last Modified",
                    ),
                ),
            ],
        ),
    ]
