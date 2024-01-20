from __future__ import annotations

from slack_sdk.web import SlackResponse

from django_slack_bot.slack_messages.backends import DummyBackend
from django_slack_bot.slack_messages.models import SlackMessage


class TestDummyBackend:
    def test_backend(self) -> None:
        backend = DummyBackend()
        assert isinstance(backend.send_message(), SlackMessage)
        assert isinstance(backend._prepare_message(), SlackMessage)
        assert isinstance(backend._send_message(), SlackResponse)
        assert backend._record_request() is None
        assert backend._record_response() is None
