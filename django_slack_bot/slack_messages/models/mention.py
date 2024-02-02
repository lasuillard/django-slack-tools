"""Message recipients model."""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from django_slack_bot.utils.model_mixins import TimestampMixin


class SlackMentionManager(models.Manager["SlackMention"]):
    """Manager for message recipients model."""


class SlackMention(TimestampMixin, models.Model):
    """People or group in channels receive messages."""

    class MentionType(models.TextChoices):
        """Possible mention types."""

        USER = "U", _("User")
        "User mentions. e.g. `@lasuillard`."

        GROUP = "G", _("Group")
        "Team mentions. e.g. `@backend`."

        SPECIAL = "S", _("Special")
        "Special mentions. e.g. `@here`, `@channel`, `@everyone`."

        UNKNOWN = "?", _("Unknown")
        "Unknown mention type."

    type = models.CharField(
        verbose_name=_("Type"),
        help_text=_("Type of mentions."),
        max_length=1,
        choices=MentionType.choices,
        blank=False,
    )
    name = models.CharField(
        verbose_name=_("Name"),
        help_text=_("Human-friendly mention name."),
        max_length=128,
    )
    mention_id = models.CharField(
        verbose_name=_("Mention ID"),
        help_text=_("User or group ID, or raw mention itself."),
        max_length=32,
    )

    objects: SlackMentionManager = SlackMentionManager()

    class Meta:  # noqa: D106
        verbose_name = _("Mention")
        verbose_name_plural = _("Mentions")

    def __str__(self) -> str:
        return _("{name} ({type}, {mention_id})").format(
            name=self.name,
            type=self.get_type_display(),
            mention_id=self.mention_id,
        )

    @property
    def mention(self) -> str:
        """Mention string for use in messages, e.g. `"<@{USER_ID}>"`."""
        if self.type == SlackMention.MentionType.USER:
            return f"<@{self.mention_id}>"

        if self.type == SlackMention.MentionType.GROUP:
            return f"<!subteam^{self.mention_id}>"

        return self.mention_id
