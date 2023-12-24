"""Message recipients model."""
from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from django_slack_bot.utils.fields import SeparatedValuesField
from django_slack_bot.utils.model_mixins import TimestampMixin


class SlackMessageRecipientManager(models.Manager["SlackMessageRecipient"]):
    """Manager for message recipients model."""


class SlackMessageRecipient(TimestampMixin, models.Model):
    """People or group in channels receive messages."""

    alias = models.CharField(
        verbose_name=_("Alias"),
        help_text=_("Alias for this recipient."),
        max_length=256,
        unique=True,
    )
    channel = models.CharField(
        verbose_name=_("Channel"),
        help_text=_("Slack channel where messages will be sent."),
        max_length=128,
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

        return _("{alias} ({channel}, {num_mentions} mentions)").format(
            alias=self.alias,
            channel=self.channel,
            num_mentions=len(mentions),
        )
