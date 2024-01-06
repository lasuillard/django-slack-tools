"""Dummy backend doing nothing."""
from __future__ import annotations

from logging import getLogger
from typing import Any

from slack_sdk.web import SlackResponse

from django_slack_bot.models import SlackMessage

from .base import BackendBase, WorkspaceInfo

logger = getLogger(__name__)


class DummyBackend(BackendBase):
    """An dummy backend that does nothing with message."""

    def get_workspace_info(self) -> WorkspaceInfo:
        """Returns meaningless, hard-coded info."""
        return WorkspaceInfo(
            team={
                "id": "-",
                "url": "https://example.com/",
            },
            members=[],
            usergroups=[],
            channels=[],
        )

    def send_message(self, *args: Any, **kwargs: Any) -> SlackMessage:  # noqa: ARG002
        """This backend will not do anything, just like dummy."""
        return SlackMessage()

    def _prepare_message(self, *args: Any, **kwargs: Any) -> SlackMessage:  # noqa: ARG002
        return SlackMessage()

    # TODO(lasuillard): Construct dummy `SlackResponse` instance and return it
    def _send_message(self, *args: Any, **kwargs: Any) -> SlackResponse:  # noqa: ARG002
        return SlackResponse(
            client=None,
            http_verb="POST",
            api_url="https://www.slack.com/api/chat.postMessage",
            req_args={},
            data={"ok": False},
            headers={},
            status_code=200,
        )

    def _record_request(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def _record_response(self, *args: Any, **kwargs: Any) -> Any:
        ...
