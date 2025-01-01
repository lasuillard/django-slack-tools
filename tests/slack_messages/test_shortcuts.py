from __future__ import annotations

from typing import TYPE_CHECKING
from unittest import mock

import pytest

from django_slack_tools.slack_messages.response import MessageResponse
from django_slack_tools.slack_messages.shortcuts import slack_message

from ._factories import SlackMessageResponseFactory

if TYPE_CHECKING:
    from unittest.mock import Mock

pytestmark = pytest.mark.django_db


def test_slack_message(mock_slack_client: Mock) -> None:
    mock_slack_client.chat_postMessage.return_value = SlackMessageResponseFactory()
    response = slack_message("whatever-channel", template="greet.xml", context={"greet": "Hello, World!"})

    assert isinstance(response, MessageResponse)
    assert (request := response.request)
    assert request.model_dump() == {
        "body": {
            "attachments": None,
            "blocks": [{"text": {"text": "Hello, World!,", "type": "mrkdwn"}, "type": "section"}],
            "icon_emoji": None,
            "icon_url": None,
            "metadata": None,
            "text": None,
            "username": None,
        },
        "channel": "whatever-channel",
        "context": {
            "greet": "Hello, World!",
        },
        "header": {
            "mrkdwn": None,
            "parse": None,
            "reply_broadcast": None,
            "thread_ts": None,
            "unfurl_links": None,
            "unfurl_media": None,
        },
        "id_": mock.ANY,
        "template_key": "greet.xml",
    }
    assert response.error is None
    assert response.data
    assert response.ts
    assert response.parent_ts is None
