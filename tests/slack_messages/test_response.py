from django_slack_tools.slack_messages.request import MessageHeader, MessageRequest
from django_slack_tools.slack_messages.response import MessageResponse
from tests.slack_messages._factories import MessageRequestFactory, MessageResponseFactory


class TestMessageResponse:
    def test_instance_creation(self) -> None:
        assert MessageResponseFactory()

    def test_str(self) -> None:
        request = MessageRequestFactory(id_="request-id")
        response = MessageResponseFactory(request=request)
        assert str(response) == "<MessageResponse:request-id>"

    def test_repr(self) -> None:
        request = MessageRequestFactory(
            id_="request-id",
            channel="some-channel",
            template_key="some-template-key",
            context={"some": "context"},
            header=MessageHeader(),
            body=None,
        )
        response = MessageResponseFactory(
            request=request,
            ok=True,
            error=None,
            data={"some": "data"},
            ts="some-ts",
            parent_ts=None,
        )
        assert (
            repr(response)
            == "MessageResponse(request=MessageRequest(id_='request-id', channel='some-channel', template_key='some-template-key', context={'some': 'context'}, header=MessageHeader(mrkdwn=None, parse=None, reply_broadcast=None, thread_ts=None, unfurl_links=None, unfurl_media=None), body=None), ok=True, error=None, data={'some': 'data'}, ts='some-ts', parent_ts=None)"  # noqa: E501
        )

    def test_eq(self) -> None:
        assert MessageResponseFactory() != -1
        request = MessageRequestFactory(
            id_="request-id",
            channel="some-channel",
            template_key="some-template-key",
            context={"some": "context"},
            header=MessageHeader(),
            body=None,
        )
        response = MessageResponseFactory(
            request=request,
            ok=True,
            error=None,
            data={"some": "data"},
            ts="some-ts",
            parent_ts=None,
        )
        assert response == MessageResponse(
            request=MessageRequest(
                id_="request-id",
                channel="some-channel",
                template_key="some-template-key",
                context={"some": "context"},
                header=MessageHeader(),
                body=None,
            ),
            ok=True,
            error=None,
            data={"some": "data"},
            ts="some-ts",
            parent_ts=None,
        )

    def test_as_dict(self) -> None:
        response = MessageResponseFactory(
            ok=True,
            error=None,
            data={"some": "data"},
            ts="some-ts",
            parent_ts=None,
        )
        assert response.as_dict() == {
            "ok": True,
            "error": None,
            "data": {"some": "data"},
            "ts": "some-ts",
            "parent_ts": None,
        }
