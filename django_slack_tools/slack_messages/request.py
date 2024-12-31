# noqa: D100
from __future__ import annotations

import uuid
from typing import Any

from django_slack_tools.utils.repr import make_repr


class MessageRequest:
    """Message request object."""

    id_: str
    channel: Any
    template_key: str
    context: dict[str, Any]
    header: MessageHeader
    body: MessageBody | None

    def __init__(  # noqa: PLR0913
        self,
        *,
        id_: str | None = None,
        channel: Any,
        template_key: str,
        context: dict[str, Any],
        header: MessageHeader,
        body: MessageBody | None = None,
    ) -> None:
        """Initialize the message request.

        Args:
            id_: Unique identifier for the message. If not provided, will be generated.
            channel: Channel to send the message to.
            template_key: Template key to use for the message.
            context: Context to render the template with.
            header: Control headers to pass to messaging backend.
            body: Body of the message.
        """
        self.id_ = id_ or self._generate_id()
        self.channel = channel
        self.template_key = template_key
        self.context = context
        self.header = header
        self.body = body

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}:{self.id_}>"

    def __repr__(self) -> str:
        return make_repr(self)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False

        return all(getattr(self, attr) == getattr(other, attr) for attr in self.__dict__)

    # TODO(lasuillard): Put `message_id` field in the database model.
    @classmethod
    def _generate_id(cls) -> str:
        return str(uuid.uuid4())

    def as_dict(self) -> dict[str, Any]:
        """Return the message request as a dictionary."""
        return {
            "id_": self.id_,
            "channel": self.channel,
            "template_key": self.template_key,
            "context": self.context,
            "header": self.header,
            "body": self.body,
        }


class MessageHeader:
    """Message header."""

    mrkdwn: str | None
    parse: str | None
    reply_broadcast: bool | None
    thread_ts: str | None
    unfurl_links: bool | None
    unfurl_media: bool | None

    def __init__(  # noqa: PLR0913
        self,
        mrkdwn: str | None = None,
        parse: str | None = None,
        reply_broadcast: bool | None = None,
        thread_ts: str | None = None,
        unfurl_links: bool | None = None,
        unfurl_media: bool | None = None,
    ) -> None:
        """Initialize the message header."""
        self.mrkdwn = mrkdwn
        self.parse = parse
        self.reply_broadcast = reply_broadcast
        self.thread_ts = thread_ts
        self.unfurl_links = unfurl_links
        self.unfurl_media = unfurl_media

    def __repr__(self) -> str:
        return make_repr(self)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False

        return all(getattr(self, attr) == getattr(other, attr) for attr in self.__dict__)

    @classmethod
    def from_any(cls, obj: MessageHeader | dict[str, Any] | None = None) -> MessageHeader:
        """Create instance from compatible types."""
        if isinstance(obj, cls):
            return obj

        if isinstance(obj, dict):
            return cls(**obj)

        if obj is None:
            return cls()

        msg = f"Unsupported type {type(obj)}"
        raise TypeError(msg)

    # TODO(lasuillard): Define TypedDict for the return type.
    def as_dict(self) -> dict[str, Any]:
        """Return the message header as a dictionary."""
        return {
            "mrkdwn": self.mrkdwn,
            "parse": self.parse,
            "reply_broadcast": self.reply_broadcast,
            "thread_ts": self.thread_ts,
            "unfurl_links": self.unfurl_links,
            "unfurl_media": self.unfurl_media,
        }


class MessageBody:
    """Message body."""

    attachments: list[dict] | None

    # See more about blocks at https://api.slack.com/reference/block-kit/blocks
    blocks: list[dict] | None

    text: str | None
    icon_emoji: str | None
    icon_url: str | None
    metadata: dict | None
    username: str | None

    def __init__(  # noqa: PLR0913
        self,
        attachments: list[dict] | None = None,
        blocks: list[dict] | None = None,
        text: str | None = None,
        icon_emoji: str | None = None,
        icon_url: str | None = None,
        metadata: dict | None = None,
        username: str | None = None,
    ) -> None:
        """Initialize the message body."""
        if not any((attachments, blocks, text)):
            msg = "At least one of `attachments`, `blocks` and `text` must set"
            raise ValueError(msg)

        self.attachments = attachments
        self.blocks = blocks
        self.text = text
        self.icon_emoji = icon_emoji
        self.icon_url = icon_url
        self.metadata = metadata
        self.username = username

    def __repr__(self) -> str:
        return make_repr(self)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False

        return all(getattr(self, attr) == getattr(other, attr) for attr in self.__dict__)

    @classmethod
    def from_any(cls, obj: str | MessageBody | dict[str, Any]) -> MessageBody:
        """Create instance from compatible types."""
        if isinstance(obj, cls):
            return obj

        if isinstance(obj, dict):
            return cls(**obj)

        if isinstance(obj, str):
            return cls(text=obj)

        msg = f"Unsupported type {type(obj)}"
        raise TypeError(msg)

    # TODO(lasuillard): Define TypedDict for the return type.
    def as_dict(self) -> dict[str, Any]:
        """Return the message body as a dictionary."""
        return {
            "attachments": self.attachments,
            "blocks": self.blocks,
            "text": self.text,
            "icon_emoji": self.icon_emoji,
            "icon_url": self.icon_url,
            "metadata": self.metadata,
            "username": self.username,
        }
