"""Slack backends actually interact with Slack API to do something."""

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, Any, Callable

from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _
from slack_bolt import App

from .base import BaseBackend

if TYPE_CHECKING:
    from slack_sdk.web import SlackResponse

    from django_slack_tools.slack_messages.request import MessageBody, MessageHeader


logger = getLogger(__name__)


class SlackBackend(BaseBackend):
    """Backend actually sending the messages."""

    def __init__(
        self,
        *,
        slack_app: App | Callable[[], App] | str,
    ) -> None:
        """Initialize backend.

        Args:
            slack_app: Slack app instance or import string.
        """
        if isinstance(slack_app, str):
            slack_app = import_string(slack_app)

        if callable(slack_app):
            slack_app = slack_app()

        if not isinstance(slack_app, App):
            msg = "Couldn't resolve provided app spec into Slack app instance."
            raise ImproperlyConfigured(msg)

        self._slack_app = slack_app

    def send_message(self, *, channel: str, header: MessageHeader, body: MessageBody) -> SlackResponse:  # noqa: D102
        return self._slack_app.client.chat_postMessage(
            channel=channel,
            **header.model_dump(),
            **body.model_dump(),
        )


class SlackRedirectBackend(SlackBackend):
    """Inherited Slack backend with redirection to specific channels."""

    def __init__(self, *, slack_app: App | str, redirect_channel: str, inform_redirect: bool = True) -> None:
        """Initialize backend.

        Args:
            slack_app: Slack app instance or import string.
            redirect_channel: Slack channel to redirect.
            inform_redirect: Whether to append an attachment informing that the message has been redirected.
                Defaults to `True`.
        """
        self.redirect_channel = redirect_channel
        self.inform_redirect = inform_redirect

        super().__init__(slack_app=slack_app)

    def send_message(self, *, channel: str, header: MessageHeader, body: MessageBody) -> SlackResponse:  # noqa: D102
        if self.inform_redirect:
            attachments = body.attachments or []
            attachments.append(
                self._make_inform_attachment(original_channel=channel),
            )
            body.attachments = attachments

        return self._slack_app.client.chat_postMessage(
            channel=self.redirect_channel,
            **header.model_dump(),
            **body.model_dump(),
        )

    def _make_inform_attachment(self, *, original_channel: str) -> dict[str, Any]:
        msg_redirect_inform = _(
            ":warning:  This message was originally sent to channel *{channel}* but redirected here.",
        )

        return {
            "color": "#eb4034",
            "text": msg_redirect_inform.format(channel=original_channel),
        }
