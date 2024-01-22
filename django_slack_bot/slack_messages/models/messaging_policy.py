"""Messaging policy model."""
from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from django_slack_bot.utils.dict_template import dict_template_validator
from django_slack_bot.utils.model_mixins import TimestampMixin
from django_slack_bot.utils.slack import header_validator

from .message_recipient import SlackMessageRecipient


class SlackMessagingPolicyManager(models.Manager["SlackMessagingPolicy"]):
    """Manager for Slack messaging policies."""


class SlackMessagingPolicy(TimestampMixin, models.Model):
    """An Slack messaging policy which determines message content and those who receive messages."""

    code = models.CharField(
        verbose_name=_("Code"),
        help_text=_("Unique message code for lookup, mostly by human."),
        max_length=32,
        unique=True,
    )
    enabled = models.BooleanField(
        verbose_name=_("Enabled"),
        help_text=_("Turn on or off current messaging policy."),
        default=True,
    )
    recipients = models.ManyToManyField(
        SlackMessageRecipient,
        verbose_name=_("Message recipients"),
        help_text=_("Those who will receive messages."),
    )
    header_defaults = models.JSONField(
        verbose_name=_("Default header"),
        help_text=_("Default header values applied to messages on creation."),
        validators=[header_validator],
        blank=True,
        default=dict,
    )
    template = models.JSONField(
        verbose_name=_("Message template object"),
        help_text=_("Dictionary-based template object."),
        validators=[dict_template_validator],
        null=True,
        blank=True,
    )
    # Type is too obvious but due to limits...
    objects: SlackMessagingPolicyManager = SlackMessagingPolicyManager()

    class Meta:  # noqa: D106
        verbose_name = _("Messaging Policy")
        verbose_name_plural = _("Messaging Policies")

    def __str__(self) -> str:
        num_recipients = self.recipients.all().count()
        if self.enabled:
            return _("{code} (enabled, {num_recipients} recipients)").format(
                code=self.code,
                num_recipients=num_recipients,
            )

        return _("{code} (disabled, {num_recipients} recipients)").format(code=self.code, num_recipients=num_recipients)
