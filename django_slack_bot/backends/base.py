"""Slack messaging backends."""
from __future__ import annotations

from abc import ABC, abstractmethod
from logging import getLogger
from typing import TYPE_CHECKING, Any, Sequence, TypedDict, cast

from slack_sdk.errors import SlackApiError

from django_slack_bot.models import SlackMessage

if TYPE_CHECKING:
    from slack_sdk.web import SlackResponse

logger = getLogger(__name__)


class BackendBase(ABC):
    """Abstract base class for backends."""

    @abstractmethod
    def get_workspace_info(self) -> WorkspaceInfo:
        """Get current Slack workspace info."""

    def send_message(  # noqa: PLR0913
        self,
        *,
        # Slack API does not use this, but user inherited classes may do something with this
        args: Sequence[Any],
        # There is no allowed cases for keyword arguments being empty
        kwargs: dict[str, Any],
        channel: str,
        raise_exception: bool,
        save_db: bool,
        record_detail: bool,
    ) -> SlackMessage | None:
        """Send Slack message.

        Args:
            args: Slack message arguments.
            kwargs: Slack message keyword arguments.
            channel: Channel to send message.
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
            response = self._send_message(*args, channel=channel, **kwargs)
        except SlackApiError as err:
            logger.exception("Error occurred while sending Slack message.")
            if raise_exception:
                raise

            response = err.response

        if not response:
            return None

        # Slack message ORM instance
        message = None

        # Suppress database exceptions too
        try:
            req_args = response.req_args
            ok = response.get("ok")
            message = SlackMessage(channel=channel, body=req_args["json"], ok=ok)
            if ok:
                # `str` if OK, otherwise `None`
                message.ts = cast(str, response.get("ts"))
                message.parent_ts = response.get("message", {}).get("thread_ts", "")  # type: ignore[call-overload]

            if record_detail:
                message.request = self._record_request(response)
                message.response = self._record_response(response)

            if save_db:
                message.save()

        except Exception:
            logger.exception("Error occurred while handling Slack message ORM instance.")
            if raise_exception:
                raise

        return message

    @abstractmethod
    def _send_message(self, *args: Any, **kwargs: Any) -> SlackResponse | None:
        """Internal implementation of actual 'send message' behavior."""

    @abstractmethod
    def _record_request(self, response: SlackResponse) -> Any:
        """Extract request data to be recorded. Should return JSON-serializable object."""

    @abstractmethod
    def _record_response(self, response: SlackResponse) -> Any:
        """Extract response data to be recorded. Should return JSON-serializable object."""


# TODO(#17): Better typing; inherit Slack app & client instance with type annotations
class WorkspaceInfo(TypedDict):
    """Slack workspace info."""

    # https://api.slack.com/methods/team.info
    team: dict

    # https://api.slack.com/methods/users.list
    members: list[dict]

    # https://api.slack.com/methods/usergroups.list
    usergroups: list[dict]

    # https://api.slack.com/methods/conversations.list
    channels: list[dict]
