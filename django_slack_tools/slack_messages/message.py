"""Handy APIs for sending Slack messages."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from django_slack_tools.app_settings import app_settings
from django_slack_tools.slack_messages.models.message_recipient import SlackMessageRecipient
from django_slack_tools.utils.slack import MessageBody, MessageHeader

from .models import SlackMessagingPolicy

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from django_slack_tools.slack_messages.backends.base import BaseBackend

    from .models import SlackMessage


def slack_message(  # noqa: PLR0913
    body: str | MessageBody | dict[str, Any],
    *,
    channel: str,
    header: MessageHeader | dict[str, Any] | None = None,
    raise_exception: bool = False,
    get_permalink: bool = False,
    backend: BaseBackend = app_settings.backend,
) -> SlackMessage:
    """Send a simple text message.

    Args:
        body: Message content, simple message or full request body.
        channel: Channel to send message.
        header: Slack message control header.
        raise_exception: Whether to re-raise caught exception while sending messages.
        get_permalink: Try to get the message permalink via extraneous Slack API calls.
        backend: Messaging backend. If not set, use `app_settings.backend`.

    Returns:
        Sent message instance or `None`.
    """
    body = MessageBody.from_any(body)
    header = MessageHeader.from_any(header)
    message = backend.prepare_message(channel=channel, header=header, body=body)

    return backend.send_message(message, raise_exception=raise_exception, get_permalink=get_permalink)


def slack_message_via_policy(  # noqa: PLR0913
    policy: str | SlackMessagingPolicy = app_settings.default_policy_code,
    *,
    header: MessageHeader | dict[str, Any] | None = None,
    raise_exception: bool = False,
    lazy: bool = False,
    get_permalink: bool = False,
    context: dict[str, Any] | None = None,
    backend: BaseBackend = app_settings.backend,
) -> int:
    """Send a simple text message.

    Some default context variables are populated and available for use in templates.
    See corresponding backend implementation for available context variables.

    Args:
        policy: Messaging policy code or policy instance. Defaults to app's default policy.
        header: Slack message control header.
        raise_exception: Whether to re-raise caught exception while sending messages.
        lazy: Decide whether try create policy with disabled, if not exists.
        get_permalink: Try to get the message permalink via extraneous Slack API calls.
        context: Dictionary to pass to template for rendering.
        backend: Messaging backend. If not set, use `app_settings.backend`.

    Returns:
        Count of messages sent successfully.

    Raises:
        SlackMessagingPolicy.DoesNotExist: Policy for given code does not exists.
    """
    if isinstance(policy, str):
        if lazy:
            policy, created = SlackMessagingPolicy.objects.get_or_create(
                code=policy,
                defaults={
                    "enabled": app_settings.lazy_policy_enabled,
                    "template": app_settings.default_template,
                },
            )
            if created:
                # Add default recipient for created policy
                recipient = SlackMessageRecipient.objects.get(alias=app_settings.default_recipient)
                policy.recipients.add(recipient)
                logger.warning("Policy for code %r created because `lazy` is set.", policy)
        else:
            policy = SlackMessagingPolicy.objects.get(code=policy)

    header = MessageHeader.from_any(header)
    context = context or {}

    messages = backend.prepare_messages_from_policy(policy, header=header, context=context)
    if not policy.enabled:
        logger.warning(
            "Created %d messages but not sending because policy %s is not enabled.",
            len(messages),
            policy.code,
        )
        return 0

    return backend.send_messages(*messages, raise_exception=raise_exception, get_permalink=get_permalink)
