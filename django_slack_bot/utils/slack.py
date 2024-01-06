"""Some utils for Slack."""
from __future__ import annotations

import json
import urllib.parse
from typing import Any, List, Optional

import pydantic
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from pydantic import BaseModel, model_validator


def get_block_kit_builder_url(*, team_id: str, blocks: dict | None = None, attachments: dict | None = None) -> str:
    """Returns URL to Slack Block Kit Builder.

    Args:
        team_id: Slack team ID.
        blocks: Message blocks. Defaults to None.
        attachments: Message attachments. Defaults to None.

    Raises:
        ValueError: Thrown if not only single value of blocks or attachments provided.

    Returns:
        URL to Block Kit Builder preview.
    """
    if (not blocks and not attachments) or (blocks and attachments):
        msg = "Only one of `blocks` or `attachments` should be provided."
        raise ValueError(msg)

    payload = {"blocks": blocks} if blocks else {"attachments": attachments} if attachments else {}
    payload_urlencoded = urllib.parse.quote(json.dumps(payload))
    return f"https://app.slack.com/block-kit-builder/{team_id}#{payload_urlencoded}"


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


def header_validator(value: Any) -> None:
    """Validate given value is valid message header."""
    try:
        MessageHeader.model_validate(value)
    except pydantic.ValidationError as exc:
        err = _convert_errors(exc)
        raise err from exc


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


def body_validator(value: Any) -> None:
    """Validate given value is valid message body."""
    try:
        MessageBody.model_validate(value)
    except pydantic.ValidationError as exc:
        err = _convert_errors(exc)
        raise err from exc


def _convert_errors(exc: pydantic.ValidationError) -> ValidationError:
    """Convert Pydantic validation error to Django error."""
    errors = [
        ValidationError(
            _("Input validation failed [msg=%(msg)r, input=%(input)r]"),
            code=", ".join(map(str, err["loc"])),  # TODO(lasuillard): Better error code
            params={
                "msg": err["msg"],
                "input": err["input"],
            },
        )
        for err in exc.errors()
    ]
    return ValidationError(errors)
