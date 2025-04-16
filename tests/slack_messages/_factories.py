from __future__ import annotations

from datetime import datetime
from typing import Any

from factory import lazy_attribute  # type: ignore[attr-defined]

from tests._factories import SlackResponseFactory


class SlackMessageResponseFactory(SlackResponseFactory):
    """Response factory for `chat.postMessage` API method."""

    @lazy_attribute
    def data(self) -> dict[str, Any]:
        ts = str(datetime.now().timestamp())  # noqa: DTZ005
        return {
            "ok": True,
            "channel": "whatever-channel",
            "ts": ts,
            "message": {
                "bot_id": "<REDACTED>",
                "type": "message",
                "text": self.text,  # type: ignore[attr-defined]
                "user": "<REDACTED>",
                "ts": ts,
                "app_id": "<REDACTED>",
                "blocks": self.blocks,  # type: ignore[attr-defined]
                "team": "<REDACTED>",
                "bot_profile": {},
                "attachments": self.attachments,  # type: ignore[attr-defined]
            },
        }

    class Params:
        text = "Hello, World!"
        blocks = [  # noqa: RUF012
            {
                "type": "rich_text",
                "block_id": "FbU8",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {
                                "type": "text",
                                "text": "Hello, World!",
                            },
                        ],
                    },
                ],
            },
        ]
        attachments = []  # type: ignore[var-annotated]  # noqa: RUF012


class SlackGetPermalinkResponseFactory(SlackResponseFactory):
    """Response factory for `chat.getPermalink` API method."""

    @lazy_attribute
    def data(self) -> dict[str, Any]:
        return {
            "ok": True,
            "channel": "whatever-channel",
            "permalink": self.permalink,  # type: ignore[attr-defined]
        }

    class Params:
        permalink = "https://ghostbusters.slack.com/archives/C1H9RESGA/p135854651500008"
