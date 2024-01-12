"""Utils for Slack messaging."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, model_validator


class MessageHeader(BaseModel):
    """Type definition for message header."""

    # NOTE: `channel` is omitted to handle it in recipients
    #       Because extra fields not forbidden for reasons, channel can be passed but not recommended

    mrkdwn: Optional[str] = None  # noqa: UP007
    parse: Optional[str] = None  # noqa: UP007
    reply_broadcast: Optional[bool] = None  # noqa: UP007
    thread_ts: Optional[str] = None  # noqa: UP007
    unfurl_links: Optional[bool] = None  # noqa: UP007
    unfurl_media: Optional[bool] = None  # noqa: UP007


class MessageBody(BaseModel):
    """Type definition for message body."""

    attachments: Optional[List[dict]] = None  # noqa: UP006, UP007

    # See more about blocks at https://api.slack.com/reference/block-kit/blocks
    blocks: Optional[List[dict]] = None  # noqa: UP006, UP007

    text: Optional[str] = None  # noqa: UP007
    icon_emoji: Optional[str] = None  # noqa: UP007
    icon_url: Optional[str] = None  # noqa: UP007
    metadata: Optional[dict] = None  # noqa: UP007
    username: Optional[str] = None  # noqa: UP007

    @model_validator(mode="after")
    def _check_one_of_exists(self) -> MessageBody:
        if not self.attachments and not self.blocks and not self.text:
            msg = "At least one of `attachments`, `blocks` and `text` must set"
            raise ValueError(msg)

        return self
