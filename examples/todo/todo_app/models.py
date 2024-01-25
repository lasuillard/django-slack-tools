from django.db import models
from django.utils.translation import gettext_lazy as _


class Todo(models.Model):
    title = models.CharField(
        verbose_name=_("Title"),
        help_text=_("Title of todo."),
        max_length=100,
    )
    description = models.TextField(
        verbose_name=_("Description"),
        help_text=_("Description of todo."),
        blank=True,
        default="",
    )
    completed = models.BooleanField(
        verbose_name=_("Completed"),
        help_text=_("Is todo completed?"),
        default=False,
    )
    created = models.DateTimeField(
        verbose_name=_("Created"),
        help_text=_("When instance created."),
        auto_now_add=True,
    )
    last_modified = models.DateTimeField(
        verbose_name=_("Last Modified"),
        help_text=_("When instance modified recently."),
        auto_now=True,
    )

    def __str__(self) -> str:
        return self.title
