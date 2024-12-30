from __future__ import annotations  # noqa: D100

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from django_slack_tools.slack_messages.request import MessageRequest


class MessageResponse:
    """Response from a messaging backend."""

    request: MessageRequest | None
    ok: bool
    error: Any | None
    data: Any
    ts: str | None
    parent_ts: str | None

    def __init__(  # noqa: PLR0913
        self,
        *,
        request: MessageRequest | None = None,
        ok: bool,
        error: Any | None = None,
        data: Any,
        ts: str | None,
        parent_ts: str | None,
    ) -> None:
        """Initialize a Response object.

        Args:
            request: The message request associated with the response.
            ok: Indicates whether the message was sent successfully.
            error: Any error information related to the response.
            data: The data associated with the response.
            ts: Identifier of the message.
            parent_ts: Identifier of the parent message.
        """
        self.request = request
        self.ok = ok
        self.error = error
        self.data = data
        self.ts = ts
        self.parent_ts = parent_ts

    def __str__(self) -> str:
        request_id = getattr(self.request, "id_", None)
        return f"<{self.__class__.__name__}:{request_id}>"

    # TODO(lasuillard): Test it can initialize object by its repr.
    def __repr__(self) -> str:
        return self.__str__()

    def as_dict(self) -> dict[str, Any]:
        """Return the response as a dictionary, except for the request."""
        return {
            "ok": self.ok,
            "error": self.error,
            "data": self.data,
        }
