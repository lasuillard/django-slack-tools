import pytest

from django_slack_tools.slack_messages.request import MessageBody, MessageHeader

from ._factories import MessageRequestFactory


class TestMessageRequest:
    # TODO(lasuillard): Implement tests for MessageRequest

    def test_instance_creation(self) -> None:
        assert MessageRequestFactory()


class TestMessageHeader:
    def test_instance_creation(self) -> None:
        assert MessageHeader()

    def test_from_any(self) -> None:
        assert MessageHeader.from_any(None) == MessageHeader()
        assert MessageHeader.from_any({"mrkdwn": "some-markdown"}) == MessageHeader(mrkdwn="some-markdown")
        with pytest.raises(TypeError, match="Unsupported type <class 'int'>"):
            MessageHeader.from_any(-1)  # type: ignore[arg-type]


class TestMessageBody:
    def test_instance_creation(self) -> None:
        assert MessageBody(text="some-text")

    def test_from_any(self) -> None:
        assert MessageBody.from_any(MessageBody(text="some-text")) == MessageBody(text="some-text")
        assert MessageBody.from_any({"text": "some-text"}) == MessageBody(text="some-text")
        assert MessageBody.from_any("some-text") == MessageBody(text="some-text")
        with pytest.raises(TypeError, match="Unsupported type <class 'int'>"):
            MessageBody.from_any(-1)  # type: ignore[arg-type]
