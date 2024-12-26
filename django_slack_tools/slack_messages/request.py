from __future__ import annotations  # noqa: D100

import uuid
from typing import Any


class MessageRequest:
    """Message request object."""

    id_: str
    recipient: Any
    template_key: str
    context: dict[str, Any]
    headers: dict[str, Any]
    body: Any

    def __init__(  # noqa: PLR0913
        self,
        *,
        id_: str | None = None,
        recipient: Any,
        template_key: str,
        context: dict[str, Any],
        headers: dict[str, Any],
        body: Any = None,
    ) -> None:
        """Initialize the message request.

        Args:
            id_: Unique identifier for the message. If not provided, will be generated.
            recipient: Recipient of the message.
            template_key: Template key to use for the message.
            context: Context to render the template with.
            headers: Control headers to pass to messaging backend.
            body: Body of the message.
        """
        self.id_ = id_ or self._generate_id()
        self.recipient = recipient
        self.template_key = template_key
        self.context = context
        self.headers = headers
        self.body = body

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}:{self.id_}>"

    # TODO(lasuillard): Test it can initialize object by its repr.
    def __repr__(self) -> str:
        return self.__str__()

    @classmethod
    def _generate_id(cls) -> str:
        return str(uuid.uuid4())

    def copy_with_overrides(self, **overrides: Any) -> MessageRequest:
        """Create a new message request with the given overrides."""
        attrs = {
            "recipient": self.recipient,
            "template_key": self.template_key,
            "context": self.context,
            "headers": self.headers,
            "body": self.body,
        }
        attrs.update(overrides)
        return MessageRequest(**attrs)

    def as_dict(self) -> dict[str, Any]:
        """Return the message request as a dictionary."""
        return {
            "id": self.id_,
            "recipient": self.recipient,
            "template_key": self.template_key,
            "context": self.context,
            "headers": self.headers,
            "body": self.body,
        }
