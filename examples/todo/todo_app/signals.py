from __future__ import annotations

from typing import Any

from django.db.models import signals
from django.dispatch import receiver

from django_slack_bot.slack_messages.message import slack_message_via_policy

from .models import Todo


@receiver(signals.post_save, sender=Todo)
def notify_slack(
    sender: type[Todo],  # noqa: ARG001
    instance: Todo,
    created: bool,  # noqa: FBT001
    **kwargs: Any,  # noqa: ARG001
) -> None:
    """Send a Slack message if new To Do created or existing instance updated."""
    if created:
        slack_message_via_policy(
            "TODO-CREATED",
            lazy=True,
            context={"title": instance.title},
        )
    else:
        slack_message_via_policy(
            "TODO-UPDATED",
            lazy=True,
            context={"title": instance.title},
        )
