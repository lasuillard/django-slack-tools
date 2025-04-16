"""Dummy backend doing nothing."""

from __future__ import annotations

from logging import getLogger
from typing import Any

from slack_sdk.web import SlackResponse

from .base import BaseBackend

logger = getLogger(__name__)


class DummyBackend(BaseBackend):
    """An dummy backend that does nothing with message."""

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
