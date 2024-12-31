import pytest

from django_slack_tools.slack_messages.request import MessageBody, MessageHeader, MessageRequest

from ._factories import MessageRequestFactory


class TestMessageRequest:
    # TODO(lasuillard): Implement tests for MessageRequest

    def test_instance_creation(self) -> None:
        assert MessageRequestFactory()

    def test_str(self) -> None:
        request = MessageRequestFactory(id_="request-id")
        assert str(request) == "<MessageRequest:request-id>"

    def test_repr(self) -> None:
        request = MessageRequestFactory(
            id_="request-id",
            channel="some-channel",
            template_key="some-template-key",
            context={"some": "context"},
            header=MessageHeader(),
            body=None,
        )
        assert (
            repr(request)
            == "MessageRequest(id_='request-id', channel='some-channel', template_key='some-template-key', context={'some': 'context'}, header=MessageHeader(mrkdwn=None, parse=None, reply_broadcast=None, thread_ts=None, unfurl_links=None, unfurl_media=None), body=None)"  # noqa: E501
        )

    def test_eq(self) -> None:
        request = MessageRequestFactory(
            id_="request-id",
            channel="some-channel",
            template_key="some-template-key",
            context={"some": "context"},
            header=MessageHeader(),
            body=None,
        )
        assert request != -1
        assert request == MessageRequest(
            id_="request-id",
            channel="some-channel",
            template_key="some-template-key",
            context={"some": "context"},
            header=MessageHeader(),
            body=None,
        )

    def test_copy_with_overrides(self) -> None:
        request = MessageRequestFactory(
            id_="request-id",
            channel="some-channel",
            template_key="some-template-key",
            context={"some": "context"},
            header=MessageHeader(),
        )

        copy = request.copy_with_overrides(channel="some-other-channel")

        assert copy is not request
        assert copy.id_ != request.id_
        assert copy.channel == "some-other-channel"
        assert copy.template_key == "some-template-key"
        assert copy.context == {"some": "context"}
        assert copy.header == MessageHeader()
        assert copy.body is None

    def test_as_dict(self) -> None:
        request = MessageRequestFactory(
            id_="request-id",
            channel="some-channel",
            template_key="some-template-key",
            context={"some": "context"},
            header=MessageHeader(),
            body=None,
        )
        assert request.as_dict() == {
            "id_": "request-id",
            "channel": "some-channel",
            "template_key": "some-template-key",
            "context": {"some": "context"},
            "header": MessageHeader(),
            "body": None,
        }


class TestMessageHeader:
    def test_instance_creation(self) -> None:
        assert MessageHeader()

    def test_repr(self) -> None:
        assert (
            repr(MessageHeader())
            == "MessageHeader(mrkdwn=None, parse=None, reply_broadcast=None, thread_ts=None, unfurl_links=None, unfurl_media=None)"  # noqa: E501
        )

    def test_eq(self) -> None:
        assert MessageHeader() != -1
        assert MessageHeader() == MessageHeader()

    def test_from_any(self) -> None:
        assert MessageHeader.from_any(None) == MessageHeader()
        assert MessageHeader.from_any({"mrkdwn": "some-markdown"}) == MessageHeader(mrkdwn="some-markdown")
        with pytest.raises(TypeError, match="Unsupported type <class 'int'>"):
            MessageHeader.from_any(-1)  # type: ignore[arg-type]


class TestMessageBody:
    def test_instance_creation(self) -> None:
        assert MessageBody(text="some-text")

    def test_repr(self) -> None:
        assert (
            repr(MessageBody(text="some-text"))
            == "MessageBody(attachments=None, blocks=None, text='some-text', icon_emoji=None, icon_url=None, metadata=None, username=None)"  # noqa: E501
        )

    def test_eq(self) -> None:
        assert MessageBody(text="some-text") != -1
        assert MessageBody(text="some-text") == MessageBody(text="some-text")

    def test_from_any(self) -> None:
        assert MessageBody.from_any(MessageBody(text="some-text")) == MessageBody(text="some-text")
        assert MessageBody.from_any({"text": "some-text"}) == MessageBody(text="some-text")
        assert MessageBody.from_any("some-text") == MessageBody(text="some-text")
        with pytest.raises(TypeError, match="Unsupported type <class 'int'>"):
            MessageBody.from_any(-1)  # type: ignore[arg-type]
