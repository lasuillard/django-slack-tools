"""Some utils for Slack."""
from __future__ import annotations

import json
import urllib.parse
from typing import TypedDict


def get_block_kit_builder_url(*, team_id: str, payload: _BlocksPayload | _AttachmentsPayload) -> str:
    """Returns URL to Slack Block Kit Builder."""
    payload_urlencoded = urllib.parse.quote(json.dumps(payload))
    return f"https://app.slack.com/block-kit-builder/{team_id}#{payload_urlencoded}"


class _BlocksPayload(TypedDict):
    blocks: dict


class _AttachmentsPayload(TypedDict):
    attachments: dict
