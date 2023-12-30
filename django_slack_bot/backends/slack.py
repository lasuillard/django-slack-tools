"""Slack backends actually interact with Slack API to do something."""
from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, Any, Callable

from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _
from slack_bolt import App

from .base import BackendBase

if TYPE_CHECKING:
    from slack_sdk.web import SlackResponse

    from .base import WorkspaceInfo

logger = getLogger(__name__)


class SlackBackend(BackendBase):
    """Backend actually sending the messages."""

    def __init__(self, *, slack_app: App | Callable[[], App] | str) -> None:
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

    # TODO(lasuillard): Cache workspace info (default an hour, allow force invalidating cache via arg)
    def get_workspace_info(self) -> WorkspaceInfo:  # noqa: D102
        team_info = self._slack_app.client.team_info()
        team_id = team_info["team"]["id"]

        return {
            "team_id": team_id,
        }

    def _send_message(self, *args: Any, **kwargs: Any) -> SlackResponse | None:
        return self._slack_app.client.chat_postMessage(*args, **kwargs)

    def _record_request(self, response: SlackResponse) -> dict[str, Any]:
        return response.req_args

    def _record_response(self, response: SlackResponse) -> dict[str, Any]:
        return {
            "http_verb": response.http_verb,
            "api_url": response.api_url,
            "status_code": response.status_code,
            "headers": response.headers,
            "data": response.data,
        }


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

    def _send_message(self, *args: Any, **kwargs: Any) -> SlackResponse | None:
        # Modify channel to force messages always sent to specific channel
        original_channel = kwargs["channel"]
        kwargs["channel"] = self.redirect_channel

        # Add an attachment that informing message has been redirected
        if self.inform_redirect:
            attachments = kwargs.get("attachments", [])
            attachments = [
                self._make_inform_attachment(original_channel=original_channel),
                *attachments,
            ]
            kwargs["attachments"] = attachments

        return super()._send_message(*args, **kwargs)

    def _make_inform_attachment(self, *, original_channel: str) -> dict[str, Any]:
        msg_redirect_inform = _(
            ":warning:  This message was originally sent to channel *{channel}* but redirected here.",
        )

        return {
            "color": "#eb4034",
            "text": msg_redirect_inform.format(channel=original_channel),
        }
