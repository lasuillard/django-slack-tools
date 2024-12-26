from __future__ import annotations  # noqa: D100

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from django_slack_tools.slack_messages.request import MessageRequest


class MessageResponse:
    """Response from a messaging backend."""

    request: MessageRequest | None
    is_sent: bool
    error: Any | None
    data: Any

    def __init__(
        self,
        *,
        request: MessageRequest | None = None,
        is_sent: bool,
        error: Any | None = None,
        data: Any,
    ) -> None:
        """Initialize a Response object.

        Args:
            request: The message request associated with the response.
            is_sent: Indicates whether the message was sent successfully.
            error: Any error information related to the response.
            data: The data associated with the response.
        """
        self.request = request
        self.is_sent = is_sent
        self.error = error
        self.data = data

    def __str__(self) -> str:
        request_id = getattr(self.request, "id_", None)
        return f"<{self.__class__.__name__}:{request_id}>"

    # TODO(lasuillard): Test it can initialize object by its repr.
    def __repr__(self) -> str:
        return self.__str__()

    def as_dict(self) -> dict[str, Any]:
        """Return the response as a dictionary, except for the request."""
        return {
            "is_sent": self.is_sent,
            "error": self.error,
            "data": self.data,
        }
