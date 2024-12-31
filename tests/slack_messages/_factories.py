from __future__ import annotations

from datetime import datetime
from typing import Any

from factory import Factory, LazyAttribute, SubFactory, lazy_attribute

from django_slack_tools.slack_messages.request import MessageHeader, MessageRequest
from django_slack_tools.slack_messages.response import MessageResponse
from tests._factories import SlackResponseFactory


class MessageRequestFactory(Factory):
    channel = "some-channel"
    template_key = "some-template-key"
    context = {"some": "context"}  # noqa: RUF012
    header = LazyAttribute(lambda _: MessageHeader())

    class Meta:
        model = MessageRequest


class MessageResponseFactory(Factory):
    request = SubFactory(MessageRequestFactory)
    ok = True
    error = None
    data = {"some": "data"}  # noqa: RUF012
    ts = "some-ts"
    parent_ts = None

    class Meta:
        model = MessageResponse


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
