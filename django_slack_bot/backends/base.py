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
    ) -> SlackMessage | None:
        """Send Slack message.

        Args:
            policy: Reference to policy created this message.
            channel: Channel to send message.
            header: Message header that controls how message will sent.
            body: Message body describing content of the message.
            raise_exception: Whether to re-raise caught exception while sending messages.
            save_db: Whether to save Slack message to database.
            record_detail: Whether to record API interaction detail, HTTP request and response details.
                Only takes effect if `save_db` is set.
                Use it with caution because request headers might contain API token.

        Returns:
            Sent Slack message or `None`.
        """
        # Send Slack message
        response: SlackResponse | None
        try:
            response = self._send_message(channel=channel, header=header, body=body)
        except SlackApiError as err:
            logger.exception("Error occurred while sending Slack message.")
            if raise_exception:
                raise

            response = err.response

        if not response:
            return None

        # Slack message ORM instance
        message = None
        ok = response.get("ok")
        message = SlackMessage(
            policy=policy,
            channel=channel,
            header=header.model_dump(),
            body=body.model_dump(),
            ok=ok,
        )
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

    @abstractmethod
    def _send_message(self, *, channel: str, header: MessageHeader, body: MessageBody) -> SlackResponse | None:
        """Internal implementation of actual 'send message' behavior."""

    @abstractmethod
    def _record_request(self, response: SlackResponse) -> Any:
        """Extract request data to be recorded. Should return JSON-serializable object."""
        # TODO(#34): Mask auth header

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
