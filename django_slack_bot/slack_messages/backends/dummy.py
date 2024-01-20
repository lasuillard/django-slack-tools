"""Dummy backend doing nothing."""
from __future__ import annotations

from logging import getLogger
from typing import Any

from slack_sdk.web import SlackResponse

from django_slack_bot.slack_messages.models import SlackMessage

from .base import BackendBase

logger = getLogger(__name__)


class DummyBackend(BackendBase):
    """An dummy backend that does nothing with message."""

    def send_message(self, *args: Any, **kwargs: Any) -> SlackMessage:  # noqa: ARG002
        """This backend will not do anything, just like dummy."""
        return SlackMessage()

    def _prepare_message(self, *args: Any, **kwargs: Any) -> SlackMessage:  # noqa: ARG002
        return SlackMessage()

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
