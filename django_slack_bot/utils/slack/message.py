"""Utils for Slack messaging."""
from __future__ import annotations

import urllib.parse
from typing import List, Optional

from pydantic import BaseModel, model_validator

from .workspace import get_workspace_info


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


def get_permalink(*, team_url: str | None = None, channel: str, ts: str, parent_ts: str) -> str | None:
    """Returns permalink to current message.

    Slack app already provides `.chat_getPermalink()` method for this purpose, but as we have
    all the necessary information, generate one for efficiency.

    Args:
        team_url: URL of current Slack team, e.g. `"https://awesome.slack.com/"`
        channel: ID of channel the message sent to.
        ts: ID of the message.
        parent_ts: Parent thread message this message replied to.

    Returns:
        Permalink to the message or `None` if not available.
    """
    if not ts:
        return None

    if team_url is None:
        workspace_info = get_workspace_info()
        team_url = "-" if workspace_info is None else workspace_info.team["url"]

    ts = "p{ts}".format(ts=ts.replace(".", ""))
    path = f"/archives/{channel}/{ts}"
    if parent_ts:
        path += f"?thread_ts={parent_ts}&cid={channel}"

    return urllib.parse.urljoin(base=team_url, url=path)
