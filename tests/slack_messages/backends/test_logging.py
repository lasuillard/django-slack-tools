from __future__ import annotations

import pytest

from django_slack_tools.slack_messages.backends import LoggingBackend
from django_slack_tools.utils.slack.message import MessageBody, MessageHeader


class TestLoggingBackend:
    pytestmark = pytest.mark.django_db()

    def test_backend(self) -> None:
        backend = LoggingBackend()
        message = backend.prepare_message(
            channel="dummy-dummy",
            header=MessageHeader(),
            body=MessageBody(text="Get some sleep"),
        )
        backend.send_message(message=message, raise_exception=True, get_permalink=True)
