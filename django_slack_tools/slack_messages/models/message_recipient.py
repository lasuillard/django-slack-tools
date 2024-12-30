"""Message recipients model."""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from django_slack_tools.utils.django.model_mixins import TimestampMixin

from .mention import SlackMention


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
        help_text=_("Slack channel ID where messages will be sent."),
        max_length=128,
        blank=False,
    )
    channel_name = models.CharField(
        verbose_name=_("Channel name"),
        help_text=_("Display name of channel."),
        max_length=256,
        blank=True,
        default="",
    )
    mentions = models.ManyToManyField(
        SlackMention,
        verbose_name=_("Mentions"),
        help_text=_("List of mentions."),
        blank=True,
    )

    objects: SlackMessageRecipientManager = SlackMessageRecipientManager()

    class Meta:  # noqa: D106
        verbose_name = _("Recipient")
        verbose_name_plural = _("Recipients")

    def __str__(self) -> str:
        num_mentions = self.mentions.count()

        return _("{alias} ({channel}, {num_mentions} mentions)").format(
            alias=self.alias,
            channel=self.channel,
            num_mentions=num_mentions,
        )
