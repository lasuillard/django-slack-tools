"""Utils for Slack messaging."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, List, Optional

NoneType = type(None)


@dataclass
class MessageHeader:
    """Message header data definition."""

    mrkdwn: Optional[str] = field(default=None)  # noqa: UP007
    parse: Optional[str] = field(default=None)  # noqa: UP007
    reply_broadcast: Optional[bool] = field(default=None)  # noqa: UP007
    thread_ts: Optional[str] = field(default=None)  # noqa: UP007
    unfurl_links: Optional[bool] = field(default=None)  # noqa: UP007
    unfurl_media: Optional[bool] = field(default=None)  # noqa: UP007

    def __post_init__(self) -> None:
        _assert_type(self.mrkdwn, (str, NoneType))
        _assert_type(self.parse, (str, NoneType))
        _assert_type(self.reply_broadcast, (bool, NoneType))
        _assert_type(self.thread_ts, (str, NoneType))
        _assert_type(self.unfurl_links, (bool, NoneType))
        _assert_type(self.unfurl_media, (bool, NoneType))

    @classmethod
    def from_any(
        cls,
        obj: MessageHeader | dict[str, Any] | None = None,
    ) -> MessageHeader:
        """Create instance from compatible types."""
        if obj is None:
            return cls()

        if isinstance(obj, dict):
            return cls(**obj)

        msg = f"Unsupported type {type(obj)}"
        raise TypeError(msg)


@dataclass
class MessageBody:
    """Data definition for message body."""

    attachments: Optional[List[dict]] = field(default=None)  # noqa: UP006, UP007

    # See more about blocks at https://api.slack.com/reference/block-kit/blocks
    blocks: Optional[List[dict]] = field(default=None)  # noqa: UP006, UP007

    text: Optional[str] = field(default=None)  # noqa: UP007
    icon_emoji: Optional[str] = field(default=None)  # noqa: UP007
    icon_url: Optional[str] = field(default=None)  # noqa: UP007
    metadata: Optional[dict] = field(default=None)  # noqa: UP007
    username: Optional[str] = field(default=None)  # noqa: UP007

    def __post_init__(self) -> None:
        _assert_type(self.attachments, (list, NoneType))
        _assert_type(self.blocks, (list, NoneType))
        _assert_type(self.text, (str, NoneType))
        _assert_type(self.icon_emoji, (str, NoneType))
        _assert_type(self.icon_url, (str, NoneType))
        _assert_type(self.metadata, (dict, NoneType))
        _assert_type(self.username, (str, NoneType))

        if not any((self.attachments, self.blocks, self.text)):
            msg = "At least one of `attachments`, `blocks` and `text` must set"
            raise ValueError(msg)

    @classmethod
    def from_any(cls, obj: str | MessageBody | dict[str, Any]) -> MessageBody:
        """Create instance from compatible types."""
        if isinstance(obj, dict):
            return cls(**obj)

        if isinstance(obj, str):
            return cls(text=obj)

        msg = f"Unsupported type {type(obj)}"
        raise TypeError(msg)


def _assert_type(obj: Any, cls: type | tuple[type, ...]) -> None:
    if not isinstance(obj, cls):
        msg = f"Invalid value type, expected {cls}, got {type(obj)}"
        raise TypeError(msg)
