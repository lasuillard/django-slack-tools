# noqa: D100
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django_slack_tools.slack_messages.models import SlackMessage, SlackMessagingPolicy
from django_slack_tools.slack_messages.request import MessageHeader, MessageRequest

from .base import BaseMiddleware

if TYPE_CHECKING:
    from django_slack_tools.slack_messages.messenger import Messenger
    from django_slack_tools.slack_messages.response import MessageResponse

logger = logging.getLogger(__name__)


class DjangoDatabasePersister(BaseMiddleware):
    """Persist message history to database. If request is `None`, will do nothing."""

    def __init__(self, *, log_level_if_no_request: int = logging.WARNING) -> None:
        """Initialize the middleware.

        Args:
            log_level_if_no_request: Log level to use if no request is found in response.
        """
        self.log_level_if_no_request = log_level_if_no_request

    def process_response(self, response: MessageResponse) -> MessageResponse | None:  # noqa: D102
        request = response.request
        if request is None:
            msg = "No request found in response, skipping persister."
            if self.log_level_if_no_request >= logging.WARNING:
                msg += " If you want to suppress this warning, set `log_level_if_no_request` to whatever you want."

            logger.log(self.log_level_if_no_request, msg)
            return response

        logger.debug("Persisting message history to database: %s", response)
        try:
            history = SlackMessage(
                channel=request.channel,
                header=request.header.as_dict(),
                body=request.body.as_dict() if request.body else {},
                ok=response.ok,
                permalink="",  # TODO(lasuillard): Re-impl this
                ts=response.ts,
                parent_ts=response.parent_ts or "",
                request=request.as_dict(),
                response=response.as_dict(),
                exception=response.error or "",
            )
            history.save()
        except Exception:
            logger.exception("Error while saving message history: %s", response)

        return response


# TODO(lasuillard): Use `to` instead of `template_key` for policy
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

    # TODO(lasuillard): Messenger centralized (lazy) configuration required to this go to the top
    #                   to resolve circular import
    #                   This is a workaround to avoid circular import for now
    @property
    def messenger(self) -> Messenger:  # noqa: D102
        from django_slack_tools.slack_messages.shortcuts import get_messenger

        if isinstance(self._messenger, str):
            self._messenger = get_messenger(self._messenger)

        return self._messenger

    def process_request(self, request: MessageRequest) -> MessageRequest | None:  # noqa: D102
        # TODO(lasuillard): Hacky way to stop the request, need to find a better way
        if request.context.get("__final__", False):
            return request

        try:
            policy = SlackMessagingPolicy.objects.get(code=request.template_key)
        except SlackMessagingPolicy.DoesNotExist:
            if self.auto_create_policy:
                # TODO(lasuillard): Provide default template (render all elements in context)
                logger.warning("No policy found for template key: %s", request.template_key)
                policy = SlackMessagingPolicy.objects.create(code=request.template_key)

            raise

        requests: list[MessageRequest] = []
        for recipient in policy.recipients.all():
            req = MessageRequest(
                channel=recipient.channel,
                template_key=policy.code,
                context={**request.context, "__final__": True},
                header=MessageHeader.from_any({**policy.header_defaults, **request.header.as_dict()}),
            )
            requests.append(req)

        for req in requests:
            self.messenger.send_request(req)

        # Stop current request
        return None
