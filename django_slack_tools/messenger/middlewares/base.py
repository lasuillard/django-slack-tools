# noqa: D100
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django_slack_tools.messenger.request import MessageRequest
    from django_slack_tools.messenger.response import MessageResponse


class BaseMiddleware:
    """Base class for middleware components."""

    def process_request(self, request: MessageRequest) -> MessageRequest | None:  # pragma: no cover
        """Process the incoming requests.

        Args:
            request: Message request.

        Returns:
            MessageRequest objects or `None`.
        """
        return request

    def process_response(self, response: MessageResponse) -> MessageResponse | None:  # pragma: no cover
        """Processes a sequence of MessageResponse objects and returns the processed sequence.

        Args:
            response: Message response.

        Returns:
            MessageResponse objects or `None`.
        """
        return response
