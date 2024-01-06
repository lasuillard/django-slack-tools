from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from django_slack_bot.backends import SlackBackend, SlackRedirectBackend
from django_slack_bot.models import SlackMessage
from django_slack_bot.utils.slack import MessageBody, MessageHeader

if TYPE_CHECKING:
    from slack_bolt import App


class TestSlackBackend:
    @pytest.mark.slack()
    @pytest.mark.vcr()
    def test_send_message(self, slack_app: App, slack_channel: str) -> None:
        backend = SlackBackend(slack_app=slack_app)
        msg = backend.send_message(
            channel=slack_channel,
            header=MessageHeader(),
            body=MessageBody(text="Hello, World!"),
            raise_exception=True,
            save_db=False,
            record_detail=True,
        )
        assert isinstance(msg, SlackMessage)
        assert "Authorization" not in msg.request["headers"]


class TestSlackRedirectBackend:
    @pytest.mark.slack()
    @pytest.mark.vcr()
    def test_send_message(self, slack_app: App, slack_channel: str) -> None:
        backend = SlackRedirectBackend(slack_app=slack_app, redirect_channel=slack_channel)
        msg = backend.send_message(
            channel="whatever-this-channel",
            header=MessageHeader(),
            body=MessageBody(text="Hello, World!"),
            raise_exception=True,
            save_db=False,
            record_detail=True,
        )
        assert isinstance(msg, SlackMessage)
