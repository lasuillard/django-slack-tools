from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.db.models import signals
from django.dispatch import receiver

from django_slack_tools.slack_messages.shortcuts import slack_message

from .models import Todo

if TYPE_CHECKING:
    from collections.abc import Iterable


@receiver(signals.post_save, sender=Todo)
def notify_for_create(
    sender: type[Todo],  # noqa: ARG001
    instance: Todo,
    created: bool,  # noqa: FBT001
    **kwargs: Any,  # noqa: ARG001
) -> None:
    """Send a Slack message if new To Do created or existing instance updated."""
    if created:
        slack_message("TODO-CREATE", context={"title": instance.title})


@receiver(signals.pre_save, sender=Todo)
def notify_for_update(
    sender: type[Todo],  # noqa: ARG001
    instance: Todo,
    update_fields: Iterable[str] | None = None,  # noqa: ARG001
    **kwargs: Any,  # noqa: ARG001
) -> None:
    """Send a Slack message if new To Do created or existing instance updated."""
    try:
        old_instance = Todo.objects.get(pk=instance.pk)  # type: ignore[attr-defined]
    except Todo.DoesNotExist:
        return

    old_values = {
        "title": old_instance.title,
        "description": old_instance.description,
        "completed": old_instance.completed,
    }
    new_values = {
        "title": instance.title,
        "description": instance.description,
        "completed": instance.completed,
    }

    slack_message("TODO-UPDATE", context={"old_values": old_values, "new_values": new_values})
