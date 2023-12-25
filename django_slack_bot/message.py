"""Handy APIs for sending Slack messages."""
from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, Any, Sequence

from django_slack_bot.utils.dict_template import render

from .app_settings import app_settings
from .models import SlackMessagingPolicy

logger = getLogger(__name__)

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


def slack(  # noqa: PLR0913
    policy: str | SlackMessagingPolicy,
    *,
    args: Sequence[Any] = (),
    kwargs: dict[str, Any] | None = None,
    raise_exception: bool = False,
    save_db: bool = True,
    record_detail: bool = False,
    **dictpl_kwargs: Any | None,
) -> list[SlackMessage | None]:
    """Send a simple text message.

    Mentions for each recipient will be passed to template as keyword `{mentions}`.
    Template should include it to use mentions.

    Args:
        policy: Messaging policy code or policy instance.
        args: Slack message arguments.
        kwargs: Slack message keyword arguments.
        raise_exception: Whether to re-raise caught exception while sending messages.
        save_db: Whether to save Slack message to database.
        record_detail: Whether to record API interaction detail, HTTP request and response details.
            Only takes effect if `save_db` is set.
            Use it with caution because request headers might contain API token.
        dictpl_kwargs: Keyword arguments passed to policy template.

    Returns:
        Sent message instance or `None`.

    Raises:
        SlackMessagingPolicy.DoesNotExist: Policy for given code does not exists.
    """
    if isinstance(policy, str):
        policy = SlackMessagingPolicy.objects.get(code=policy)

    kwargs = kwargs or {}

    template = policy.template

    messages: list[SlackMessage | None] = []
    for recipient in policy.recipients.all():
        mentions = ", ".join(recipient.mentions.values_list("mention", flat=True))

        dictpl_kwargs.setdefault("mentions", mentions)
        if "mentions" in dictpl_kwargs:
            logger.warning(
                "Template keyword argument `mentions` is reserved for passing mentions, but already exists."
                " It will be overridden by user provided value.",
            )

        body = render(template, **dictpl_kwargs)
        kwargs = {
            **body,
            **kwargs,
        }

        message = app_settings.backend.send_message(
            args=args,
            kwargs=kwargs,
            channel=recipient.channel,
            raise_exception=raise_exception,
            save_db=save_db,
            record_detail=record_detail,
        )
        messages.append(message)

    return messages
