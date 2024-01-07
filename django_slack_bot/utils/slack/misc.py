"""Miscellaneous features."""
from __future__ import annotations

import json
import urllib.parse


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