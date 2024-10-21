"""Celery utils."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone

from django_slack_tools.slack_messages import message
from django_slack_tools.slack_messages.models import SlackMessage

if TYPE_CHECKING:
    from typing import Any

logger = get_task_logger(__name__)


@shared_task
def slack_message(
    body: str | dict[str, Any],
    *,
    channel: str,
    header: dict[str, Any] | None = None,
    raise_exception: bool = False,
    get_permalink: bool = False,
) -> int | None:
    """Celery task wrapper for `message.slack_message`.

    Args:
        body: Message content, simple message or full request body.
        channel: Channel to send message.
        header: Slack message control header.
        raise_exception: Whether to re-raise caught exception while sending messages.
        get_permalink: Try to get the message permalink via extraneous Slack API calls.

    Returns:
        ID of sent message.
    """
    sent_msg = message.slack_message(
        body,
        channel=channel,
        header=header,
        raise_exception=raise_exception,
        get_permalink=get_permalink,
    )
    return sent_msg.id


@shared_task
def slack_message_via_policy(  # noqa: PLR0913
    policy: str,
    *,
    header: dict[str, Any] | None = None,
    raise_exception: bool = False,
    lazy: bool = False,
    get_permalink: bool = False,
    context: dict[str, Any] | None = None,
) -> int:
    """Celery task wrapper for `message.slack_message_via_policy`.

    Args:
        policy: Messaging policy code.
        header: Slack message control header.
        raise_exception: Whether to re-raise caught exception while sending messages.
        lazy: Decide whether try to create policy with disabled, if not exists.
        get_permalink: Try to get the message permalink via extraneous Slack API calls.
        context: Context variables for message rendering.

    Returns:
        Number of sent messages.
    """
    return message.slack_message_via_policy(
        policy,
        header=header,
        raise_exception=raise_exception,
        lazy=lazy,
        get_permalink=get_permalink,
        context=context,
    )


@shared_task
def cleanup_old_messages(
    *,
    base_ts: str | None = None,
    threshold_seconds: int | None = 7 * 24 * 60 * 60,  # 7 days
) -> int:
    """Delete old messages created before given threshold.

    Args:
        threshold_seconds: Threshold seconds. Defaults to 7 days.
        base_ts: Base timestamp to calculate the threshold, in ISO format. If falsy, current timestamp will be used.

    Returns:
        Number of deleted messages.
    """
    if base_ts:
        dt = datetime.fromisoformat(base_ts)
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt)
    else:
        dt = timezone.localtime()

    if threshold_seconds is None:
        logger.warning("Threshold seconds not provided, skipping cleanup.")
        return 0

    cleanup_threshold = dt - timedelta(seconds=threshold_seconds)
    logger.debug("Cleaning up messages older than %s.", cleanup_threshold)

    num_deleted, _ = SlackMessage.objects.filter(created__lt=cleanup_threshold).delete()
    logger.info("Deleted %d old messages.", num_deleted)

    return num_deleted
