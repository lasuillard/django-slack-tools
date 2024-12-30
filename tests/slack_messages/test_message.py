from __future__ import annotations

from typing import TYPE_CHECKING
from unittest import mock

import pytest

from django_slack_tools.slack_messages.message import slack_message
from django_slack_tools.slack_messages.response import MessageResponse

from ._factories import SlackMessageResponseFactory

if TYPE_CHECKING:
    from unittest.mock import Mock

pytestmark = pytest.mark.django_db


def test_slack_message(mock_slack_client: Mock) -> None:
    mock_slack_client.chat_postMessage.return_value = SlackMessageResponseFactory()
    response = slack_message("whatever-channel", template="greet.xml", context={"greet": "Hello, World!"})

    assert isinstance(response, MessageResponse)
    request = response.request
    assert request
    assert request.as_dict() == {
        "body": mock.ANY,
        "channel": "whatever-channel",
        "context": {
            "greet": "Hello, World!",
        },
        "header": mock.ANY,
        "id": mock.ANY,
        "template_key": "greet.xml",
    }
    assert request.body
    assert request.body.as_dict() == {
        "attachments": None,
        "blocks": [{"text": {"text": "Hello, World!,", "type": "mrkdwn"}, "type": "section"}],
        "icon_emoji": None,
        "icon_url": None,
        "metadata": None,
        "text": None,
        "username": None,
    }
    assert request.header.as_dict() == {
        "mrkdwn": None,
        "parse": None,
        "reply_broadcast": None,
        "thread_ts": None,
        "unfurl_links": None,
        "unfurl_media": None,
    }
    assert response.error is None
    assert response.data
    assert response.ts
    assert response.parent_ts is None
