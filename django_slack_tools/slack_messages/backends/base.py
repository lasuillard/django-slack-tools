"""Slack messaging backends."""

from __future__ import annotations

import traceback
from abc import ABC, abstractmethod
from logging import getLogger
from typing import TYPE_CHECKING, Any, Optional, cast

from slack_sdk.errors import SlackApiError

from django_slack_tools.slack_messages.response import MessageResponse

if TYPE_CHECKING:
    from slack_sdk.web import SlackResponse

    from django_slack_tools.slack_messages.request import MessageBody, MessageHeader, MessageRequest


logger = getLogger(__name__)


class BaseBackend(ABC):
    """Abstract base class for messaging backends."""

    def deliver(self, request: MessageRequest) -> MessageResponse:
        """Deliver message request."""
        if request.body is None:
            msg = "Message body is required."
            raise ValueError(msg)

        try:
            response = self._send_message(
                channel=request.channel,
                header=request.header,
                body=request.body,
            )
            error = None
        except SlackApiError as err:
            response = err.response
            error = traceback.format_exc()

        ok = cast(bool, response.get("ok"))
        data: Any
        if ok:
            ts = cast(Optional[str], response.get("ts", None))
            data = response.get("message", {})
            parent_ts = data.get("thread_ts", None)
        else:
            ts = None
            data = response.data
            parent_ts = None

        return MessageResponse(
            request=request,
            ok=ok,
            error=error,
            data=data,
            ts=ts,
            parent_ts=parent_ts,
        )

    @abstractmethod
    def _send_message(self, *, channel: str, header: MessageHeader, body: MessageBody) -> SlackResponse:
        """Internal implementation of actual 'send message' behavior."""
