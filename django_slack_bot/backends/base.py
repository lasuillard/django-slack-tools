"""Slack messaging backends."""
from __future__ import annotations

from abc import ABC, abstractmethod
from logging import getLogger
from typing import TYPE_CHECKING, Any, List, cast

from pydantic import BaseModel
from slack_sdk.errors import SlackApiError

from django_slack_bot.models import SlackMessage, SlackMessagingPolicy

if TYPE_CHECKING:
    from slack_sdk.web import SlackResponse

    from django_slack_bot.utils.slack import MessageBody, MessageHeader

logger = getLogger(__name__)

# TODO(#10): Celery backend to send messages


class BackendBase(ABC):
    """Abstract base class for backends."""

    @abstractmethod
    def get_workspace_info(self) -> WorkspaceInfo:
        """Get current Slack workspace info."""

    def send_message(  # noqa: PLR0913
        self,
        *,
        policy: SlackMessagingPolicy | None = None,
        channel: str,
        header: MessageHeader,
        body: MessageBody,
        raise_exception: bool,
        save_db: bool,
        record_detail: bool,
    ) -> SlackMessage:
        """Send Slack message.

        Args:
            policy: Messaging policy to create message with.
            channel: Channel to send message.
            header: Message header that controls how message will sent.
            body: Message body describing content of the message.
            raise_exception: Whether to re-raise caught exception while sending messages.
            save_db: Whether to save Slack message changes.
            record_detail: Whether to record API interaction detail, HTTP request and response details.
                Would take effect only if `save_db` set `True`.
                Also, existing data will be overwritten (if message has been sent already).

        Returns:
            Sent Slack message or `None`.
        """
        message = self._prepare_message(policy=policy, channel=channel, header=header, body=body)

        # Send Slack message
        response: SlackResponse
        try:
            response = self._send_message(message=message)
        except SlackApiError as err:
            if raise_exception:
                raise

            logger.exception(
                "Error occurred while sending Slack message, but ignored because `raise_exception` not set.",
            )
            response = err.response

        # Update message detail
        ok = response.get("ok")
        message.ok = ok
        if ok:
            # `str` if OK, otherwise `None`
            message.ts = cast(str, response.get("ts"))
            message.parent_ts = response.get("message", {}).get("thread_ts", "")  # type: ignore[call-overload]

        if record_detail:
            message.request = self._record_request(response)
            message.response = self._record_response(response)

        if save_db:
            message.save()

        return message

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


class WorkspaceInfo(BaseModel):
    """Slack workspace info."""

    # https://api.slack.com/methods/team.info
    team: dict

    # https://api.slack.com/methods/users.list
    members: List[dict]  # noqa: UP006

    # https://api.slack.com/methods/usergroups.list
    usergroups: List[dict]  # noqa: UP006

    # https://api.slack.com/methods/conversations.list
    channels: List[dict]  # noqa: UP006
