"""Handy APIs for sending Slack messages."""
from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, Any

from django_slack_bot.app_settings import app_settings
from django_slack_bot.utils.dict_template import render
from django_slack_bot.utils.slack import MessageBody, MessageHeader

from .models import SlackMessagingPolicy

logger = getLogger(__name__)

if TYPE_CHECKING:
    from .models import SlackMention, SlackMessage


def slack_message(  # noqa: PLR0913
    body: str | MessageBody | dict[str, Any],
    *,
    channel: str,
    header: MessageHeader | dict[str, Any] | None = None,
    raise_exception: bool = False,
    save_db: bool = True,
    record_detail: bool = False,
    get_permalink: bool = False,
) -> SlackMessage | None:
    """Send a simple text message.

    Args:
        body: Message content, simple message or full request body.
        channel: Channel to send message.
        header: Slack message control header.
        raise_exception: Whether to re-raise caught exception while sending messages.
        save_db: Whether to save Slack message to database.
        record_detail: Whether to record API interaction detail, HTTP request and response details.
            Only takes effect if `save_db` is set.
            Use it with caution because request headers might contain API token.
        get_permalink: Try to get the message permalink via extraneous Slack API calls.

    Returns:
        Sent message instance or `None`.
    """
    # If body is just an string, make a simple message body
    body = MessageBody(text=body) if isinstance(body, str) else MessageBody.model_validate(body)
    header = MessageHeader.model_validate(header or {})

    return app_settings.backend.send_message(
        channel=channel,
        header=header,
        body=body,
        raise_exception=raise_exception,
        save_db=save_db,
        record_detail=record_detail,
        get_permalink=get_permalink,
    )


def slack_message_via_policy(  # noqa: PLR0913
    policy: str | SlackMessagingPolicy,
    *,
    header: MessageHeader | dict[str, Any] | None = None,
    raise_exception: bool = False,
    save_db: bool = True,
    record_detail: bool = False,
    lazy: bool = False,
    get_permalink: bool = False,
    **kwargs: Any | None,
) -> list[SlackMessage | None]:
    """Send a simple text message.

    Mentions for each recipient will be passed to template as keyword `{mentions}`.
    Template should include it to use mentions.

    Args:
        policy: Messaging policy code or policy instance.
        header: Slack message control header.
        raise_exception: Whether to re-raise caught exception while sending messages.
        save_db: Whether to save Slack message to database.
        record_detail: Whether to record API interaction detail, HTTP request and response details.
            Only takes effect if `save_db` is set.
            Use it with caution because request headers might contain API token.
        lazy: Decide whether try create policy with disabled, if not exists.
        get_permalink: Try to get the message permalink via extraneous Slack API calls.
        kwargs: Arbitrary keyword arguments passed to policy template.

    Returns:
        Sent message instance or `None`.

    Raises:
        SlackMessagingPolicy.DoesNotExist: Policy for given code does not exists.
    """
    if isinstance(policy, str):
        if lazy:
            policy, created = SlackMessagingPolicy.objects.get_or_create(code=policy, defaults={"enabled": False})
            if created:
                logger.warning("Policy for code %r created because `lazy` is set.", policy)
        else:
            policy = SlackMessagingPolicy.objects.get(code=policy)

    if not policy.enabled:
        return []

    header = MessageHeader.model_validate(header or {})

    # Prepare template
    template = policy.template
    overridden_reserved = {"mentions", "mentions_as_str"} & set(kwargs.keys())
    if overridden_reserved:
        logger.warning(
            "Template keyword argument(s) %s reserved for passing mentions, but already exists."
            " User provided value will override it.",
            ", ".join(f"`{s}`" for s in overridden_reserved),
        )

    messages: list[SlackMessage | None] = []
    for recipient in policy.recipients.all():
        # Auto-generated reserved kwargs
        mentions: list[SlackMention] = list(recipient.mentions.all())
        mentions_as_str = ", ".join(mention.mention for mention in mentions)

        # Render and send message
        rendered = render(template, mentions=mentions, mentions_as_str=mentions_as_str, **kwargs)
        body = MessageBody.model_validate(rendered)
        message = app_settings.backend.send_message(
            policy=policy,
            channel=recipient.channel,
            header=header,
            body=body,
            raise_exception=raise_exception,
            save_db=save_db,
            record_detail=record_detail,
            get_permalink=get_permalink,
        )
        messages.append(message)

    return messages
