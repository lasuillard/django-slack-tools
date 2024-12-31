"""Handy APIs for sending Slack messages."""
# TODO(lasuillard): Rename this module to `shortcuts.py`

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from django_slack_tools.app_settings import app_settings
from django_slack_tools.slack_messages.messenger import Messenger
from django_slack_tools.slack_messages.middlewares import DjangoDatabasePersister
from django_slack_tools.slack_messages.request import MessageHeader
from django_slack_tools.slack_messages.template_loaders import DjangoPolicyTemplateLoader, DjangoTemplateLoader

if TYPE_CHECKING:
    from django_slack_tools.slack_messages.response import MessageResponse

logger = logging.getLogger(__name__)


_MESSENGERS = {
    "default": Messenger(
        template_loaders=[
            DjangoTemplateLoader(),
            DjangoPolicyTemplateLoader(),
        ],
        middlewares=[
            DjangoDatabasePersister(),
        ],
        messaging_backend=app_settings.backend,
    ),
}


# TODO(lasuillard): Add support for multiple backends with centralized configuration
def get_messenger(name: str | None) -> Messenger:
    """Get a messenger instance by name."""
    name = name or "default"
    return _MESSENGERS[name]


def slack_message(
    to: str,
    *,
    messenger_name: str | None = None,
    template: str,
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
