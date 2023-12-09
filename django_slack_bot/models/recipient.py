"""Message recipients model."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, List

from django.db import models
from django.utils.translation import gettext_lazy as _


class SeparatedValuesField(models.TextField):
    """Custom field for storing list of string items."""

    def __init__(self, *args: Any, separator: str | None = None, **kwargs: Any) -> None:  # noqa: D107
        self.separator = separator or ","
        super().__init__(*args, **kwargs)

    def deconstruct(self) -> Any:  # noqa: D102
        name, path, args, kwargs = super().deconstruct()
        if self.separator != ",":
            kwargs["separator"] = self.separator

        return name, path, args, kwargs

    def from_db_value(self, value: Any, expression: Any, connection: Any) -> Any:  # noqa: ARG002, D102
        return self.to_python(value)

    def to_python(self, value: str | list | None) -> list[str]:  # noqa: D102
        if not value:
            return None

        if isinstance(value, list):
            return value

        return value.split(self.separator)

    def get_db_prep_value(self, value: list[str] | None) -> str | None:  # noqa: D102
        if not value:
            return None

        return self.separator.join(value)


class Recipient(models.Model):
    """People or group in channels receive messages."""

    channel = models.CharField(
        verbose_name=_("Channel"),
        help_text=_("Slack channel where messages will be sent."),
        max_length=32,
    )
    mentions = SeparatedValuesField(
        verbose_name=_("Mentions"),
        help_text=_("List of mentions, user or groups in Slack ID (e.g. U06A2DMBTTJ)."),
    )

    class Meta:  # noqa: D106
        verbose_name = _("Recipient")
        verbose_name_plural = _("Recipients")

    def __str__(self) -> str:  # noqa: D105
        if TYPE_CHECKING:
            assert isinstance(self.mentions, List[str])

        return _("{channel} ({num_mentions} mentions)").format(
            channel=self.channel,
            num_mentions=len(self.mentions),
        )
