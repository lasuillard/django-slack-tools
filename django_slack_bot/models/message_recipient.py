"""Message recipients model."""
from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from django_slack_bot.utils.fields import SeparatedValuesField


class SlackMessageRecipientManager(models.Manager["SlackMessageRecipient"]):
    """Manager for message recipients model."""


class SlackMessageRecipient(models.Model):
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

    objects: SlackMessageRecipientManager = SlackMessageRecipientManager()

    class Meta:  # noqa: D106
        verbose_name = _("Recipient")
        verbose_name_plural = _("Recipients")

    def __str__(self) -> str:  # noqa: D105
        mentions: list[str] = self.mentions

        return _("{channel} ({num_mentions} mentions)").format(
            channel=self.channel,
            num_mentions=len(mentions),
        )
