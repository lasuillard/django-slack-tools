"""Message model."""
from django.db import models
from django.utils.translation import gettext_lazy as _

from .messaging_policy import MessagingPolicy


# When message created, python template string should be strictly evaluated
# --- all arguments ({arg}) should be provided
class Message(models.Model):
    """An Slack message."""

    policy = models.ForeignKey(
        MessagingPolicy,
        verbose_name=_("Messaging Policy"),
        help_text=_("Messaging policy for this message."),
        null=True,  # Message can be built from scratch without using templates
        on_delete=models.SET_NULL,
    )

    # TODO(lasuillard): Message content

    is_sent = models.BooleanField(
        verbose_name=_("Sent"),
        help_text=_("Whether this message sent."),
        default=False,
    )

    # As ID assigned by Slack, `ts` and `parent_ts` known after received response
    ts = models.CharField(
        verbose_name=_("Message ID"),
        help_text=_("ID of an Slack message."),
        max_length=32,
        unique=True,
        default="",
    )
    parent_ts = models.CharField(
        verbose_name=_("Thread ID"),
        help_text=_("ID of current conversation thread."),
        max_length=32,
        db_index=True,
        default="",
    )

    # TODO(lasuillard): Detailed call history(req/resp) recording for debugging, with turn on/off

    class Meta:  # noqa: D106
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")

    def __str__(self) -> str:  # noqa: D105
        if self.is_sent:
            return _("Message {id} {ts} (Sent)").format(id=self.id, ts=self.ts)

        return _("Message {id} (Not sent)").format(id=self.id)
