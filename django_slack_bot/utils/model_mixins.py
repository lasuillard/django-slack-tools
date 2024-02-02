"""Django model mixins."""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class TimestampMixin(models.Model):
    """Django model mixin for created and modified timestamp fields."""

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

    class Meta:  # noqa: D106
        abstract = True
