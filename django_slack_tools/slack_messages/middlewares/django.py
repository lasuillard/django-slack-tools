# noqa: D100
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from slack_bolt import App
from slack_sdk.errors import SlackApiError

from django_slack_tools.slack_messages.models import SlackMessage, SlackMessagingPolicy
from django_slack_tools.slack_messages.request import MessageHeader, MessageRequest

from .base import BaseMiddleware

if TYPE_CHECKING:
    from django_slack_tools.slack_messages.messenger import Messenger
    from django_slack_tools.slack_messages.response import MessageResponse

logger = logging.getLogger(__name__)


class DjangoDatabasePersister(BaseMiddleware):
    """Persist message history to database. If request is `None`, will do nothing."""

    def __init__(
        self,
        *,
        slack_app: App | None = None,
        get_permalink: bool = False,
        log_level_if_no_request: int = logging.WARNING,
    ) -> None:
        """Initialize the middleware.

        Args:
            slack_app: Slack app instance to use for certain tasks, such as getting permalinks.
            get_permalink: If `True`, will try to get the permalink of the message.
            log_level_if_no_request: Log level to use if no request is found in response.
        """
        if get_permalink and not isinstance(slack_app, App):
            msg = "`slack_app` must be an instance of `App` if `get_permalink` is set `True`."
            raise ValueError(msg)

        self.slack_app = slack_app
        self.get_permalink = get_permalink
        self.log_level_if_no_request = log_level_if_no_request

    def process_response(self, response: MessageResponse) -> MessageResponse | None:  # noqa: D102
        request = response.request
        if request is None:
            msg = "No request found in response, skipping persister."
            if self.log_level_if_no_request >= logging.WARNING:
                msg += " If you want to suppress this warning, set `log_level_if_no_request` to whatever you want."

            logger.log(self.log_level_if_no_request, msg)
            return response

        logger.debug("Getting permalink for message: %s", response)
        if self.get_permalink:  # noqa: SIM108
            permalink = self._get_permalink(channel=request.channel, ts=response.ts)
        else:
            permalink = ""

        logger.debug("Persisting message history to database: %s", response)
        try:
            history = SlackMessage(
                id=request.id_,
                channel=request.channel,
                header=request.header.model_dump(),
                body=request.body.model_dump() if request.body else {},
                ok=response.ok,
                permalink=permalink,
                ts=response.ts,
                parent_ts=response.parent_ts or "",
                request=request.model_dump(),
                response=response.model_dump(exclude={"request"}),
                exception=response.error or "",
            )
            history.save()
        except Exception:
            logger.exception("Error while saving message history: %s", response)

        return response

    def _get_permalink(self, *, channel: str, ts: str | None) -> str:
        """Get permalink of the message. It returns empty string on error."""
        if not self.slack_app:
            logger.warning("Slack app not provided, cannot get permalink.")
            return ""

        if not ts:
            logger.warning("No message ts provided, cannot get permalink.")
            return ""

        try:
            response = self.slack_app.client.chat_getPermalink(channel=channel, message_ts=ts)
            return response.get("permalink", default="")
        except SlackApiError as err:
            logger.debug("Error while getting permalink: %s", exc_info=err)
            return ""


class DjangoDatabasePolicyHandler(BaseMiddleware):
    """Middleware to handle Slack messaging policies from the database."""

    def __init__(self, *, messenger: Messenger | str, auto_create_policy: bool = False) -> None:
        """Initialize the middleware.

        This middleware will load the policy from the database and send the message to all recipients.

        Args:
            messenger: Messenger instance or name to use for sending messages.
            auto_create_policy: If `True`, will create a policy if not found in the database.
        """
        self._messenger = messenger
        self.auto_create_policy = auto_create_policy

    # * It's not desirable to put import in the method,
    # * but it's the only way to avoid circular imports for now (what's the fix?)
    @property
    def messenger(self) -> Messenger:
        """Get the messenger instance. If it's a string, will get the messenger from the app settings."""
        if isinstance(self._messenger, str):
            from django_slack_tools.app_settings import get_messenger

            self._messenger = get_messenger(self._messenger)

        return self._messenger

    def process_request(self, request: MessageRequest) -> MessageRequest | None:  # noqa: D102
        # TODO(lasuillard): Hacky way to stop the request, need to find a better way
        #                   Some extra field (request.meta) could be added to share control context
        if request.context.get("__final__", False):
            return request

        code = request.channel
        try:
            policy = SlackMessagingPolicy.objects.get(code=code)
        except SlackMessagingPolicy.DoesNotExist:
            if self.auto_create_policy:
                # TODO(lasuillard): Provide default template (render all elements in context)
                logger.warning("No policy found for template key, creating one: %s", code)
                policy = SlackMessagingPolicy.objects.create(code=code)

            raise

        if not policy.enabled:
            logger.debug("Policy %s is disabled, skipping further messaging", policy)
            return None

        requests: list[MessageRequest] = []
        for recipient in policy.recipients.all():
            req = MessageRequest(
                channel=recipient.channel,
                template_key=policy.code,
                context={**request.context, "__final__": True},
                # TODO(lasuillard): Want some cleaner way to merge models
                header=MessageHeader.from_any({**policy.header_defaults, **request.header.model_dump()}),
            )
            requests.append(req)

        for req in requests:
            self.messenger.send_request(req)

        # Stop current request
        return None
