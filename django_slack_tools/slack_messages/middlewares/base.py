from __future__ import annotations  # noqa: D100

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django_slack_tools.slack_messages.request import MessageRequest
    from django_slack_tools.slack_messages.response import MessageResponse


class BaseMiddleware:
    """Base class for middleware components."""

    def process_request(self, request: MessageRequest) -> MessageRequest | None:
        """Process the incoming requests.

        Args:
            request: Message request.

        Returns:
            MessageRequest objects or `None`.
        """
        return request

    def process_response(self, response: MessageResponse) -> MessageResponse | None:
        """Processes a sequence of MessageResponse objects and returns the processed sequence.

        Args:
            response: Message response.

        Returns:
            MessageResponse objects or `None`.
        """
        return response
