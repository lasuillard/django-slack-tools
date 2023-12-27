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

        TEAM = "T", _("Team")
        "Team mentions. e.g. `@backend`."

        RAW = "R", _("Raw")
        "System mentions (e.g. `@everyone`) and raw mentions controlled by users. No processing will be applied to this type of mentions."  # noqa: E501
        # https://slack.com/help/articles/202009646-Notify-a-channel-or-workspace

    type = models.CharField(  # noqa: A003
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
    mention = models.CharField(
        verbose_name=_("Mention"),
        help_text=_("Internal mention ID for Slack."),
        max_length=32,
    )

    objects: SlackMentionManager = SlackMentionManager()

    class Meta:  # noqa: D106
        verbose_name = _("Mention")
        verbose_name_plural = _("Mentions")

    def __str__(self) -> str:  # noqa: D105
        return _("{name} ({mention}, {type})").format(
            name=self.name,
            mention=self.mention,
            type=self.get_type_display(),
        )
