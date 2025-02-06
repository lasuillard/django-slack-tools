from __future__ import annotations

from typing import Any

from django.db.models import signals
from django.dispatch import receiver

from django_slack_tools.slack_messages.shortcuts import slack_message

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
        slack_message("", template="TODO-CREATED", context={"title": instance.title})
    else:
        slack_message("", template="TODO-UPDATED", context={"title": instance.title})
