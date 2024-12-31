# noqa: D100
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django_slack_tools.slack_messages.models import SlackMessage

from .base import BaseMiddleware

if TYPE_CHECKING:
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
                header=request.header,
                body=request.body,
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
