from __future__ import annotations

from datetime import datetime
from typing import Any

from factory import lazy_attribute

from tests._factories import SlackResponseFactory


class SlackMessageResponseFactory(SlackResponseFactory):
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
                "text": self.text,
                "user": "<REDACTED>",
                "ts": ts,
                "app_id": "<REDACTED>",
                "blocks": self.blocks,
                "team": "<REDACTED>",
                "bot_profile": {},
                "attachments": self.attachments,
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
