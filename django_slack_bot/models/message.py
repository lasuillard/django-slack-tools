"""Message model."""
from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from .messaging_policy import SlackMessagingPolicy


# When message created, python template string should be strictly evaluated
# --- all arguments ({arg}) should be provided
class SlackMessage(models.Model):
    """An Slack message."""

    policy = models.ForeignKey(
        SlackMessagingPolicy,
        verbose_name=_("Messaging Policy"),
        help_text=_("Messaging policy for this message."),
        null=True,  # Message can be built from scratch without using templates
        on_delete=models.SET_NULL,
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

    # As ID assigned by Slack, `ts` and `parent_ts` known after received response
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

    class Meta:  # noqa: D106
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")

    def __str__(self) -> str:  # noqa: D105
        if self.ok is True:
            return _("Message {id} {ts} (OK)").format(id=self.id, ts=self.ts)

        if self.ok is False:
            return _("Message {id} (Not OK)").format(id=self.id)

        return _("Message {id} (Not sent)").format(id=self.id)
