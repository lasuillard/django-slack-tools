"""Slack backends actually interact with Slack API to do something."""
from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, Any, Callable

from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _
from slack_bolt import App

from django_slack_bot.utils.cache import generate_cache_key

from .base import BackendBase, WorkspaceInfo

if TYPE_CHECKING:
    from slack_sdk.web import SlackResponse

    from django_slack_bot.utils.slack import MessageBody, MessageHeader


logger = getLogger(__name__)


class SlackBackend(BackendBase):
    """Backend actually sending the messages."""

    def __init__(self, *, slack_app: App | Callable[[], App] | str, workspace_cache_timeout: int = 60 * 60) -> None:
        """Initialize backend.

        Args:
            slack_app: Slack app instance or import string.
            workspace_cache_timeout: Cache timeout for workspace information, in seconds.
                Defaults to an hour.
        """
        if isinstance(slack_app, str):
            slack_app = import_string(slack_app)

        if callable(slack_app):
            slack_app = slack_app()

        if not isinstance(slack_app, App):
            msg = "Couldn't resolve provided app spec into Slack app instance."
            raise ImproperlyConfigured(msg)

        self._slack_app = slack_app
        self._workspace_cache_timeout = workspace_cache_timeout

    # TODO(lasuillard): Increase the warm-up performance by calling API in parallel
    def get_workspace_info(self) -> WorkspaceInfo:  # noqa: D102
        cache_key = generate_cache_key(self.get_workspace_info.__name__)
        if cached := cache.get(cache_key):
            return WorkspaceInfo.model_validate(cached)

        team: dict = self._slack_app.client.team_info().get("team", default={})

        # TODO(lasuillard): For large workspace (users > 200?) it should handle pagination in future
        #                   but not considering it for now
        members: list[dict] = self._slack_app.client.users_list().get("members", default=[])
        usergroups: list[dict] = self._slack_app.client.usergroups_list().get("usergroups", default=[])
        channels: list[dict] = self._slack_app.client.conversations_list().get("channels", default=[])

        info = WorkspaceInfo(
            team=team,
            members=members,
            usergroups=usergroups,
            channels=channels,
        )
        cache.set(key=cache_key, value=info.model_dump(), timeout=self._workspace_cache_timeout)
        return info

    def _send_message(self, *, channel: str, header: MessageHeader, body: MessageBody) -> SlackResponse | None:
        return self._slack_app.client.chat_postMessage(channel=channel, **header.model_dump(), **body.model_dump())

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

    def _send_message(self, *, channel: str, body: MessageBody, **kwargs: Any) -> SlackResponse | None:
        # Modify channel to force messages always sent to specific channel
        # Add an attachment that informing message has been redirected
        if self.inform_redirect:
            body.attachments = [
                self._make_inform_attachment(original_channel=channel),
                *(body.attachments or []),
            ]

        return super()._send_message(channel=self.redirect_channel, body=body, **kwargs)

    def _make_inform_attachment(self, *, original_channel: str) -> dict[str, Any]:
        msg_redirect_inform = _(
            ":warning:  This message was originally sent to channel *{channel}* but redirected here.",
        )

        return {
            "color": "#eb4034",
            "text": msg_redirect_inform.format(channel=original_channel),
        }
