"""Handy APIs for sending Slack messages."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, overload

from django_slack_tools.app_settings import get_messenger
from django_slack_tools.slack_messages.request import MessageBody, MessageHeader, MessageRequest

if TYPE_CHECKING:
    from django_slack_tools.slack_messages.response import MessageResponse

logger = logging.getLogger(__name__)


@overload
def slack_message(
    to: str,
    *,
    messenger_name: str | None = None,
    header: MessageHeader | dict[str, Any] | None = None,
    message: str,
) -> MessageResponse | None: ...  # pragma: no cover


@overload
def slack_message(
    to: str,
    *,
    messenger_name: str | None = None,
    header: MessageHeader | dict[str, Any] | None = None,
    template: str,
    context: dict[str, Any] | None = None,
) -> MessageResponse | None: ...  # pragma: no cover


def slack_message(  # noqa: PLR0913
    to: str,
    *,
    messenger_name: str | None = None,
    header: MessageHeader | dict[str, Any] | None = None,
    template: str | None = None,
    context: dict[str, Any] | None = None,
    message: str | None = None,
) -> MessageResponse | None:
    """Shortcut for sending a Slack message.

    Args:
        to: Recipient.
        messenger_name: Messenger name. If not set, default messenger is used.
        header: Slack message control header.
        template: Message template key. Cannot be used with `message`.
        context: Context for rendering the template. Only used with `template`.
        message: Simple message text. Cannot be used with `template`.

    Returns:
        Sent message instance or `None`.
    """
    if (template and message) or (not template and not message):
        msg = "Either `template` or `message` must be set, but not both."
        raise ValueError(msg)

    messenger = get_messenger(messenger_name)
    header = MessageHeader.from_any(header)

    if message:
        request = MessageRequest(
            channel=to,
            header=header,
            body=MessageBody(text=message),
            template_key=None,
            context={},
        )
        return messenger.send_request(request)

    context = context or {}
    return messenger.send(to, header=header, template=template, context=context)
