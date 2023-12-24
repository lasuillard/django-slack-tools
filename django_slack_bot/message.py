"""Handy APIs for sending Slack messages."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Sequence

from .app_settings import app_settings

if TYPE_CHECKING:
    from .models import SlackMessage


def slack_message(  # noqa: PLR0913
    body: str | dict[str, Any],
    *,
    args: Sequence[Any] = (),
    kwargs: dict[str, Any] | None = None,
    channel: str,
    raise_exception: bool = False,
    save_db: bool = True,
    record_detail: bool = False,
) -> SlackMessage | None:
    """Send a simple text message.

    Args:
        body: Message content, simple message or full request body.
        args: Slack message arguments.
        kwargs: Slack message keyword arguments.
        channel: Channel to send message.
        raise_exception: Whether to re-raise caught exception while sending messages.
        save_db: Whether to save Slack message to database.
        record_detail: Whether to record API interaction detail, HTTP request and response details.
            Only takes effect if `save_db` is set.
            Use it with caution because request headers might contain API token.

    Returns:
        Sent message instance or `None`.
    """
    kwargs = kwargs or {}

    # If body is just an string, make a simple message body
    if isinstance(body, str):
        kwargs = {
            "text": body,
            **kwargs,
        }

    return app_settings.backend.send_message(
        args=args,
        kwargs=kwargs,
        channel=channel,
        raise_exception=raise_exception,
        save_db=save_db,
        record_detail=record_detail,
    )
