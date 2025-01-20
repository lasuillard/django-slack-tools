"""Handy APIs for sending Slack messages."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from django_slack_tools.app_settings import get_messenger
from django_slack_tools.slack_messages.request import MessageHeader

if TYPE_CHECKING:
    from django_slack_tools.slack_messages.response import MessageResponse

logger = logging.getLogger(__name__)


def slack_message(
    to: str,
    *,
    messenger_name: str | None = None,
    template: str | None = None,
    header: MessageHeader | dict[str, Any] | None = None,
    context: dict[str, Any] | None = None,
) -> MessageResponse | None:
    """Shortcut for sending a Slack message.

    Args:
        to: Recipient.
        messenger_name: Messenger name. If not set, default messenger is used.
        template: Message template key.
        header: Slack message control header.
        context: Context for rendering the template.

    Returns:
        Sent message instance or `None`.
    """
    messenger = get_messenger(messenger_name)
    header = MessageHeader.from_any(header)
    context = context or {}
    return messenger.send(to, template=template, header=header, context=context)
