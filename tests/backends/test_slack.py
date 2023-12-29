from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from django_slack_bot.backends import SlackBackend, SlackRedirectBackend
from django_slack_bot.models import SlackMessage

if TYPE_CHECKING:
    from slack_bolt import App


class TestSlackBackend:
    @pytest.mark.slack()
    @pytest.mark.vcr()
    def test_send_message(self, slack_app: App, slack_channel: str) -> None:
        backend = SlackBackend(slack_app=slack_app)
        msg = backend.send_message(
            args=(),
            kwargs={"text": "Hello, World!"},
            channel=slack_channel,
            raise_exception=True,
            save_db=False,
            record_detail=True,
        )
        assert isinstance(msg, SlackMessage)


class TestSlackRedirectBackend:
    @pytest.mark.slack()
    @pytest.mark.vcr()
    def test_send_message(self, slack_app: App, slack_channel: str) -> None:
        backend = SlackRedirectBackend(slack_app=slack_app, redirect_channel=slack_channel)
        msg = backend.send_message(
            args=(),
            kwargs={"text": "Hello, World!"},
            channel="whatever-this-channel",
            raise_exception=True,
            save_db=False,
            record_detail=True,
        )
        assert isinstance(msg, SlackMessage)
