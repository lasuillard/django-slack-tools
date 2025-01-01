# noqa: D100
# flake8: noqa: UP006, UP007, UP035; Subscription syntax available since Python 3.10
from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class MessageRequest(BaseModel):
    """Message request object."""

    model_config = ConfigDict(extra="forbid")

    id_: str = Field(default_factory=lambda: str(uuid.uuid4()))
    channel: Any
    template_key: str
    context: Dict[str, Any]
    header: MessageHeader
    body: Optional[MessageBody] = None


class MessageHeader(BaseModel):  # noqa: D101
    model_config = ConfigDict(extra="forbid")

    mrkdwn: Optional[str] = None
    parse: Optional[str] = None
    reply_broadcast: Optional[bool] = None
    thread_ts: Optional[str] = None
    unfurl_links: Optional[bool] = None
    unfurl_media: Optional[bool] = None

    @classmethod
    def from_any(cls, obj: MessageHeader | dict[str, Any] | None = None) -> MessageHeader:
        """Create instance from compatible types."""
        if isinstance(obj, cls):
            return obj

        if isinstance(obj, dict):
            return cls.model_validate(obj)

        if obj is None:
            return cls()

        msg = f"Unsupported type {type(obj)}"
        raise TypeError(msg)


class MessageBody(BaseModel):  # noqa: D101
    model_config = ConfigDict(extra="forbid")

    attachments: Optional[List[dict]] = None

    # See more about blocks at https://api.slack.com/reference/block-kit/blocks
    blocks: Optional[list[dict]] = None

    text: Optional[str] = None
    icon_emoji: Optional[str] = None
    icon_url: Optional[str] = None
    metadata: Optional[dict] = None
    username: Optional[str] = None

    @model_validator(mode="after")
    def _check_at_least_one_field_is_set(self) -> MessageBody:
        if not any((self.attachments, self.blocks, self.text)):
            msg = "At least one of `attachments`, `blocks` and `text` must set"
            raise ValueError(msg)

        return self

    @classmethod
    def from_any(cls, obj: str | MessageBody | dict[str, Any]) -> MessageBody:
        """Create instance from compatible types."""
        if isinstance(obj, cls):
            return obj

        if isinstance(obj, dict):
            return cls.model_validate(obj)

        if isinstance(obj, str):
            return cls(text=obj)

        msg = f"Unsupported type {type(obj)}"
        raise TypeError(msg)
