"""Slack backends actually interact with Slack API to do something."""
from __future__ import annotations

import traceback
from logging import getLogger
from typing import TYPE_CHECKING, Any, Callable, cast

from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _
from slack_bolt import App
from slack_sdk.errors import SlackApiError

from .base import BackendBase

if TYPE_CHECKING:
    from slack_sdk.web import SlackResponse

    from django_slack_bot.slack_messages.models import SlackMessage, SlackMessagingPolicy
    from django_slack_bot.utils.slack import MessageBody, MessageHeader


logger = getLogger(__name__)


class SlackBackend(BackendBase):
    """Backend actually sending the messages."""

    def __init__(
        self,
        *,
        slack_app: App | Callable[[], App] | str,
        remove_auth_header: bool = True,
    ) -> None:
        """Initialize backend.

        Args:
            slack_app: Slack app instance or import string.
            workspace_cache_timeout: Cache timeout for workspace information, in seconds.
                Defaults to an hour.
            remove_auth_header: Whether to remove auth header from request headers on recording.
                Enabled by default.
        """
        if isinstance(slack_app, str):
            slack_app = import_string(slack_app)

        if callable(slack_app):
            slack_app = slack_app()

        if not isinstance(slack_app, App):
            msg = "Couldn't resolve provided app spec into Slack app instance."
            raise ImproperlyConfigured(msg)

        self._slack_app = slack_app
        self._remove_auth_header = remove_auth_header

    # TODO(lasuillard): Certainly need some refactoring here, too complex
    def send_message(  # noqa: PLR0913, C901, PLR0912
        self,
        message: SlackMessage | None = None,
        *,
        policy: SlackMessagingPolicy | None = None,
        channel: str | None = None,
        header: MessageHeader | None = None,
        body: MessageBody | None = None,
        raise_exception: bool,
        save_db: bool,
        record_detail: bool,
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
            save_db: Whether to save Slack message changes.
            record_detail: Whether to record API interaction detail, HTTP request and response details.
                Would take effect only if `save_db` set `True`.
                Also, existing data will be overwritten (if message has been sent already).
            get_permalink: Try to get the message permalink via extraneous Slack API calls.

        Returns:
            Sent Slack message.
        """
        if not message:
            if not (channel and header and body):
                msg = (
                    "Call signature mismatch for overload."
                    " If `message` not provided, `channel`, `header` and `body` all must given."
                )
                raise TypeError(msg)

            message = self._prepare_message(policy=policy, channel=channel, header=header, body=body)

        try:
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
            ok: bool | None = response.get("ok")
            message.ok = ok
            if ok:
                # `str` if OK, otherwise `None`
                message.ts = cast(str, response.get("ts"))
                message.parent_ts = response.get("message", {}).get("thread_ts", "")  # type: ignore[call-overload]
                if get_permalink:
                    message.permalink = self._get_permalink(
                        channel=message.channel,
                        message_ts=message.ts,
                        raise_exception=raise_exception,
                    )

            if record_detail:
                message.request = self._record_request(response)
                message.response = self._record_response(response)
        except:
            if record_detail:
                message.exception = traceback.format_exc()

            # Don't omit raise with flag `raise_exception` here
            raise
        finally:
            if save_db:
                message.save()

        return message

    def _get_permalink(self, *, channel: str, message_ts: str, raise_exception: bool = False) -> str:
        """Get a permalink for given message identifier."""
        try:
            _permalink_resp = self._slack_app.client.chat_getPermalink(
                channel=channel,
                message_ts=message_ts,
            )
        except SlackApiError:
            if raise_exception:
                raise

            logger.exception(
                "Error occurred while sending retrieving message's permalink,"
                " but ignored as `raise_exception` not set.",
            )
            return ""

        return _permalink_resp.get("permalink", default="")

    def _send_message(self, *, message: SlackMessage) -> SlackResponse:
        return self._slack_app.client.chat_postMessage(channel=message.channel, **message.header, **message.body)

    def _record_request(self, response: SlackResponse) -> dict[str, Any]:
        if self._remove_auth_header:
            response.req_args["headers"].pop("Authorization", None)

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

    def _prepare_message(self, *args: Any, channel: str, body: MessageBody, **kwargs: Any) -> SlackMessage:
        # Modify channel to force messages always sent to specific channel
        # Add an attachment that informing message has been redirected
        if self.inform_redirect:
            body.attachments = [
                self._make_inform_attachment(original_channel=channel),
                *(body.attachments or []),
            ]

        return super()._prepare_message(*args, channel=self.redirect_channel, body=body, **kwargs)

    def _make_inform_attachment(self, *, original_channel: str) -> dict[str, Any]:
        msg_redirect_inform = _(
            ":warning:  This message was originally sent to channel *{channel}* but redirected here.",
        )

        return {
            "color": "#eb4034",
            "text": msg_redirect_inform.format(channel=original_channel),
        }
