"""Slack messaging backends."""

from __future__ import annotations

from abc import ABC, abstractmethod
from logging import getLogger
from typing import TYPE_CHECKING, Any, overload

from django_slack_tools.slack_messages.models import SlackMessage, SlackMessagingPolicy

if TYPE_CHECKING:
    from slack_sdk.web import SlackResponse

    from django_slack_tools.utils.slack import MessageBody, MessageHeader

logger = getLogger(__name__)


class BaseBackend(ABC):
    """Abstract base class for messaging backends."""

    @overload
    def send_message(
        self,
        message: SlackMessage,
        *,
        raise_exception: bool,
        get_permalink: bool = False,
    ) -> SlackMessage: ...  # pragma: no cover

    @overload
    def send_message(
        self,
        *,
        policy: SlackMessagingPolicy | None = None,
        channel: str,
        header: MessageHeader,
        body: MessageBody,
        raise_exception: bool,
        get_permalink: bool = False,
    ) -> SlackMessage: ...  # pragma: no cover

    @abstractmethod
    def send_message(  # noqa: PLR0913
        self,
        message: SlackMessage | None = None,
        *,
        policy: SlackMessagingPolicy | None = None,
        channel: str | None = None,
        header: MessageHeader | None = None,
        body: MessageBody | None = None,
        raise_exception: bool,
        get_permalink: bool = False,
    ) -> SlackMessage:
        """Send Slack message.

        Args:
            message: Externally prepared message.
                If not given, make one using `channel`, `header` and `body` parameters.
            policy: Messaging policy to create message with.
            channel: Channel to send message.
            header: Message header that controls how message will sent.
            body: Message body describing content of the message.
            raise_exception: Whether to re-raise caught exception while sending messages.
            get_permalink: Try to get the message permalink via extraneous Slack API calls.

        Returns:
            Sent Slack message.
        """

    def _prepare_message(
        self,
        *,
        policy: SlackMessagingPolicy | None = None,
        channel: str,
        header: MessageHeader,
        body: MessageBody,
    ) -> SlackMessage:
        _header: dict = policy.header_defaults if policy else {}
        _header.update(header.model_dump(exclude_unset=True))
        _body = body.model_dump()
        return SlackMessage(policy=policy, channel=channel, header=_header, body=_body)

    @abstractmethod
    def _send_message(self, *, message: SlackMessage) -> SlackResponse:
        """Internal implementation of actual 'send message' behavior."""

    @abstractmethod
    def _record_request(self, response: SlackResponse) -> Any:
        """Extract request data to be recorded. Should return JSON-serializable object."""

    @abstractmethod
    def _record_response(self, response: SlackResponse) -> Any:
        """Extract response data to be recorded. Should return JSON-serializable object."""
