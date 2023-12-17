"""Message model."""
from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from .messaging_policy import SlackMessagingPolicy


class SlackMessageManager(models.Manager["SlackMessage"]):
    """Manager for Slack messages."""


class SlackMessage(models.Model):
    """An Slack message."""

    policy = models.ForeignKey(
        SlackMessagingPolicy,
        verbose_name=_("Messaging Policy"),
        help_text=_("Messaging policy for this message."),
        null=True,  # Message can be built from scratch without using templates
        on_delete=models.SET_NULL,
    )
    channel = models.CharField(
        verbose_name=_("Channel"),
        help_text=_("Channel name this message sent to."),
        blank=False,
        max_length=128,  # Maximum length of channel name is 80 characters
    )
    body = models.JSONField(
        verbose_name=_("Body"),
        help_text=_("Message body."),
    )
    ok = models.BooleanField(
        verbose_name=_("OK"),
        help_text=_("Whether Slack API respond with OK. If never sent, will be `null`."),
        null=True,
        default=None,
    )

    # As ID, `ts` assigned by Slack, it is known after received response
    # By known, `ts` refers to timestamp (Format of `datetime.timestamp()`, e.g. `"1702737142.945359"`)
    ts = models.CharField(
        verbose_name=_("Message ID"),
        help_text=_("ID of an Slack message."),
        max_length=32,
        default="",
    )
    parent_ts = models.CharField(
        verbose_name=_("Thread ID"),
        help_text=_("ID of current conversation thread."),
        max_length=32,
        default="",
    )

    # TODO(lasuillard): Detailed call history(req/resp) recording for debugging, with turn on/off
    request = models.JSONField(
        verbose_name=_("Request"),
        help_text=_("Dump of request content for debugging."),
        null=True,
    )
    response = models.JSONField(
        verbose_name=_("Response"),
        help_text=_("Dump of response content for debugging."),
        null=True,
    )

    objects: SlackMessageManager = SlackMessageManager()

    class Meta:  # noqa: D106
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")

    def __str__(self) -> str:  # noqa: D105
        if self.ok is True:
            return _("Message {id} {ts} (OK)").format(id=self.id, ts=self.ts)

        if self.ok is False:
            return _("Message {id} (Not OK)").format(id=self.id)

        return _("Message {id} (Not sent)").format(id=self.id)
