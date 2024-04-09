"""Handy APIs for sending Slack messages."""

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, Any

from django_slack_tools.app_settings import app_settings
from django_slack_tools.utils.dict_template import render
from django_slack_tools.utils.slack import MessageBody, MessageHeader

from .models import SlackMessagingPolicy

logger = getLogger(__name__)

if TYPE_CHECKING:
    from .models import SlackMention, SlackMessage


def slack_message(
    body: str | MessageBody | dict[str, Any],
    *,
    channel: str,
    header: MessageHeader | dict[str, Any] | None = None,
    raise_exception: bool = False,
    get_permalink: bool = False,
) -> SlackMessage | None:
    """Send a simple text message.

    Args:
        body: Message content, simple message or full request body.
        channel: Channel to send message.
        header: Slack message control header.
        raise_exception: Whether to re-raise caught exception while sending messages.
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
        get_permalink=get_permalink,
    )

RESERVED_CONTEXT_KWARGS = frozenset({"mentions", "mentions_as_str"})
DEFAULT_POLICY_CODE = "DEFAULT"

def slack_message_via_policy(  # noqa: PLR0913
    policy: str | SlackMessagingPolicy | None = None,
    *,
    header: MessageHeader | dict[str, Any] | None = None,
    raise_exception: bool = False,
    lazy: bool = False,
    get_permalink: bool = False,
    context: dict[str, Any] | None = None,
) -> list[SlackMessage | None]:
    """Send a simple text message.

    Mentions for each recipient will be passed to template as keyword `{mentions}`.
    Template should include it to use mentions.

    Args:
        policy: Messaging policy code or policy instance.
        header: Slack message control header.
        raise_exception: Whether to re-raise caught exception while sending messages.
        lazy: Decide whether try create policy with disabled, if not exists.
        get_permalink: Try to get the message permalink via extraneous Slack API calls.
        context: Dictionary to pass to template for rendering.

    Returns:
        Sent message instance or `None`.

    Raises:
        SlackMessagingPolicy.DoesNotExist: Policy for given code does not exists.
    """
    if not policy:
        policy = DEFAULT_POLICY_CODE

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
    context = context or {}

    # Prepare template
    template = policy.template
    overridden_reserved = RESERVED_CONTEXT_KWARGS & set(context.keys())
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

        # Prepare rendering arguments
        kwargs = {"mentions": mentions, "mentions_as_str": mentions_as_str}
        kwargs.update(context)

        # Render and send message
        rendered = render(template, **kwargs)
        body = MessageBody.model_validate(rendered)
        message = app_settings.backend.send_message(
            policy=policy,
            channel=recipient.channel,
            header=header,
            body=body,
            raise_exception=raise_exception,
            get_permalink=get_permalink,
        )
        messages.append(message)

    return messages
