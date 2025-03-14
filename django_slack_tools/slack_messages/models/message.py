"""Message model."""

from __future__ import annotations

import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from django_slack_tools.slack_messages.validators import body_validator, header_validator
from django_slack_tools.utils.django.model_mixins import TimestampMixin

from .messaging_policy import SlackMessagingPolicy


class SlackMessageManager(models.Manager["SlackMessage"]):
    """Manager for Slack messages."""


class SlackMessage(TimestampMixin, models.Model):
    """An Slack message."""

    id = models.CharField(primary_key=True, unique=True, max_length=255, default=uuid.uuid4, editable=False)
    policy = models.ForeignKey(
        SlackMessagingPolicy,
        verbose_name=_("Messaging Policy"),
        help_text=_("Messaging policy for this message."),
        null=True,  # Message can be built from scratch without using templates
        blank=True,
        on_delete=models.SET_NULL,
    )
    channel = models.CharField(
        verbose_name=_("Channel"),
        help_text=_("ID of channel this message sent to."),
        blank=False,
        max_length=128,  # Maximum length of channel name is 80 characters
    )
    header = models.JSONField(
        verbose_name=_("Header"),
        help_text=_(
            "Slack control arguments."
            " Allowed fields are `mrkdwn`, `parse`, `reply_broadcast`, `thread_ts`, `unfurl_links`, `unfurl_media`.",
        ),
        validators=[header_validator],
    )
    body = models.JSONField(
        verbose_name=_("Body"),
        help_text=_(
            "Message body."
            " Allowed fields are `attachments`, `body`, `text`, `icon_emoji`, `icon_url`, `metadata`, `username`.",
        ),
        validators=[body_validator],
    )
    ok = models.BooleanField(
        verbose_name=_("OK"),
        help_text=_("Whether Slack API respond with OK. If never sent, will be `null`."),
        null=True,
        default=None,
    )
    permalink = models.CharField(
        verbose_name=_("Permalink"),
        help_text=_("Permanent link for this message."),
        max_length=256,
        default="",
        blank=True,
    )

    # As ID, `ts` assigned by Slack, it is known after received response
    # By known, `ts` refers to timestamp (Format of `datetime.timestamp()`, e.g. `"1702737142.945359"`)
    ts = models.CharField(
        verbose_name=_("Message ID"),
        help_text=_("ID of an Slack message."),
        max_length=32,
        null=True,
        blank=True,
        unique=True,
    )
    parent_ts = models.CharField(
        verbose_name=_("Thread ID"),
        help_text=_("ID of current conversation thread."),
        max_length=32,
        default="",
        blank=True,
    )

    # Extraneous call detail for debugging
    request = models.JSONField(
        verbose_name=_("Request"),
        help_text=_("Dump of request content for debugging."),
        null=True,
        blank=True,
    )
    response = models.JSONField(
        verbose_name=_("Response"),
        help_text=_("Dump of response content for debugging."),
        null=True,
        blank=True,
    )
    exception = models.TextField(
        verbose_name=_("Exception"),
        help_text=_("Exception message if any."),
        blank=True,
    )

    objects: SlackMessageManager = SlackMessageManager()

    class Meta:  # noqa: D106
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")
        ordering = ("-created",)

    def __str__(self) -> str:
        if self.ok is True:
            return _("Message ({ts}, OK)").format(id=self.id, ts=self.ts)

        if self.ok is False:
            return _("Message ({id}, not OK)").format(id=self.id)

        return _("Message ({id}, not sent)").format(id=self.id)
