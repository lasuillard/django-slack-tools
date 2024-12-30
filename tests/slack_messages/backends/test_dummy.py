from __future__ import annotations

import pytest

from django_slack_tools.slack_messages.backends import DummyBackend
from django_slack_tools.slack_messages.request import MessageBody, MessageHeader, MessageRequest
from django_slack_tools.slack_messages.response import MessageResponse


class TestDummyBackend:
    pytestmark = pytest.mark.django_db()

    @pytest.fixture
    def backend(self) -> DummyBackend:
        return DummyBackend()

    def test_deliver(self, backend: DummyBackend) -> None:
        request = MessageRequest(
            channel="test-channel",
            template_key="__any__",
            context={},
            header=MessageHeader(),
            body=MessageBody(text="Hello, World!"),
        )
        response = backend.deliver(request)

        assert isinstance(response, MessageResponse)
        assert response.request is request
        assert response.ok is True
        assert response.error is None
        assert response.data == {}
        assert response.ts is None
        assert response.parent_ts is None
