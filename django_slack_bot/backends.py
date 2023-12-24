"""Slack messaging backends."""
from __future__ import annotations

from abc import ABC, abstractmethod
from logging import getLogger
from typing import TYPE_CHECKING, Any, Callable, Sequence, cast

from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _
from slack_bolt import App
from slack_sdk.errors import SlackApiError

from .models import SlackMessage

if TYPE_CHECKING:
    from slack_sdk.web import SlackResponse

logger = getLogger(__name__)


class BackendBase(ABC):
    """Abstract base class for backends."""

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


class DummyBackend(BackendBase):
    """An dummy backend that does nothing with message."""

    def send_message(self, *args: Any, **kwargs: Any) -> None:
        """This backend will not do anything, just like dummy."""

    def _send_message(self, *args: Any, **kwargs: Any) -> SlackResponse | None:
        ...

    def _record_request(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def _record_response(self, *args: Any, **kwargs: Any) -> Any:
        ...


class LoggingBackend(BackendBase):
    """Backend that log the message rather than sending it."""

    def _send_message(self, *args: Any, **kwargs: Any) -> None:
        logger.debug("Sending an message with following args=%r, kwargs=%r", args, kwargs)

    def _record_request(self, *args: Any, **kwargs: Any) -> Any:
        logger.debug("Recording request with args=%r, kwargs=%r", args, kwargs)

    def _record_response(self, *args: Any, **kwargs: Any) -> Any:
        logger.debug("Recording response with args=%r, kwargs=%r", args, kwargs)


class SlackBackend(BackendBase):
    """Backend actually sending the messages."""

    def __init__(self, *, slack_app: App | Callable[[], App] | str) -> None:
        """Initialize backend.

        Args:
            slack_app: Slack app instance or import string.
        """
        if isinstance(slack_app, str):
            slack_app = import_string(slack_app)

        if callable(slack_app):
            slack_app = slack_app()

        if not isinstance(slack_app, App):
            msg = "Couldn't resolve provided app spec into Slack app instance."
            raise ImproperlyConfigured(msg)

        self._slack_app = slack_app

    def _send_message(self, *args: Any, **kwargs: Any) -> SlackResponse | None:
        return self._slack_app.client.chat_postMessage(*args, **kwargs)

    def _record_request(self, response: SlackResponse) -> dict[str, Any]:
        return response.req_args

    def _record_response(self, response: SlackResponse) -> dict[str, Any]:
        return {
            "http_verb": response.http_verb,
            "api_url": response.api_url,
            "status_code": response.status_code,
            "headers": response.headers,
            "data": response.data,
        }


class SlackRedirectBackend(SlackBackend):
    """Inherited Slack backend with redirection to specific channels."""

    def __init__(self, *, slack_app: App | str, redirect_channel: str, inform_redirect: bool = True) -> None:
        """Initialize backend.

        Args:
            slack_app: Slack app instance or import string.
            redirect_channel: Slack channel to redirect.
            inform_redirect: Whether to append an attachment informing that the message has been redirected.
                Defaults to `True`.
        """
        self.redirect_channel = redirect_channel
        self.inform_redirect = inform_redirect

        super().__init__(slack_app=slack_app)

    def _send_message(self, *args: Any, **kwargs: Any) -> SlackResponse | None:
        # Modify channel to force messages always sent to specific channel
        original_channel = kwargs["channel"]
        kwargs["channel"] = self.redirect_channel

        # Add an attachment that informing message has been redirected
        if self.inform_redirect:
            attachments = kwargs.get("attachments", [])
            attachments = [
                self._make_inform_attachment(original_channel=original_channel),
                *attachments,
            ]
            kwargs["attachments"] = attachments

        return super()._send_message(*args, **kwargs)

    def _make_inform_attachment(self, *, original_channel: str) -> dict[str, Any]:
        msg_redirect_inform = _(
            ":warning:  This message was originally sent to channel *{channel}* but redirected here.",
        )

        return {
            "color": "#eb4034",
            "text": msg_redirect_inform.format(channel=original_channel),
        }
