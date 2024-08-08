"""Dummy backend doing nothing."""

from __future__ import annotations

from logging import getLogger
from typing import Any

from slack_sdk.web import SlackResponse

from django_slack_tools.slack_messages.models import SlackMessage

from .base import BaseBackend

logger = getLogger(__name__)


class DummyBackend(BaseBackend):
    """An dummy backend that does nothing with message."""

    def prepare_message(self, *args: Any, **kwargs: Any) -> SlackMessage:  # noqa: D102, ARG002
        return SlackMessage(header={}, body={})

    def _send_message(self, *args: Any, **kwargs: Any) -> SlackResponse:  # noqa: ARG002
        return SlackResponse(
            client=None,
            http_verb="POST",
            api_url="https://www.slack.com/api/chat.postMessage",
            req_args={},
            data={"ok": True},
            headers={},
            status_code=200,
        )

    def _get_permalink(self, *, message: SlackMessage, raise_exception: bool) -> str:  # noqa: ARG002
        return ""

    def _record_request(self, *args: Any, **kwargs: Any) -> Any: ...

    def _record_response(self, *args: Any, **kwargs: Any) -> Any: ...
