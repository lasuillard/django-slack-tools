"""Logging backend that do logging otherwise nothing."""

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, Any

from .dummy import DummyBackend

if TYPE_CHECKING:
    from slack_sdk.web import SlackResponse


logger = getLogger(__name__)


class LoggingBackend(DummyBackend):
    """Backend that log the message rather than sending it."""

    def _send_message(self, *args: Any, **kwargs: Any) -> SlackResponse:
        logger.debug("Sending an message with following args=%r, kwargs=%r", args, kwargs)
        return super()._send_message(*args, **kwargs)

    def _record_request(self, *args: Any, **kwargs: Any) -> Any:
        logger.debug("Recording request with args=%r, kwargs=%r", args, kwargs)

    def _record_response(self, *args: Any, **kwargs: Any) -> Any:
        logger.debug("Recording response with args=%r, kwargs=%r", args, kwargs)
