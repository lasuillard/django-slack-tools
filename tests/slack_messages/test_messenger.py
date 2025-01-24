from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, cast
from unittest import mock

import pytest

from django_slack_tools.slack_messages.backends import DummyBackend
from django_slack_tools.slack_messages.message_templates import PythonTemplate
from django_slack_tools.slack_messages.messenger import Messenger
from django_slack_tools.slack_messages.middlewares import (
    BaseMiddleware,
    DjangoDatabasePersister,
    DjangoDatabasePolicyHandler,
)
from django_slack_tools.slack_messages.request import MessageHeader, MessageRequest
from django_slack_tools.slack_messages.template_loaders import (
    BaseTemplateLoader,
    DjangoPolicyTemplateLoader,
    DjangoTemplateLoader,
)
from tests.slack_messages._factories import MessageRequestFactory

if TYPE_CHECKING:
    from django_slack_tools.slack_messages.response import MessageResponse


class TestMessenger:
    def test_instance_creation(self) -> None:
        """Test various instance creation scenarios."""
        # Ideal case
        kwargs: dict[str, Any] = {
            "template_loaders": [
                DjangoTemplateLoader(),
                DjangoPolicyTemplateLoader(),
            ],
            "middlewares": [
                DjangoDatabasePersister(),
                DjangoDatabasePolicyHandler(messenger="default"),
            ],
            "messaging_backend": _MockBackend(),
        }
        Messenger(**kwargs)

        # All template loaders should be inherited from `BaseTemplateLoader`
        with pytest.raises(
            TypeError,
            match=r"Expected inherited from <class '.+\.BaseTemplateLoader'>, got <class 'object'>",
        ):
            Messenger(**(kwargs | {"template_loaders": [DjangoTemplateLoader(), object()]}))

        # All middlewares should be inherited from `BaseMiddleware`
        with pytest.raises(
            TypeError,
            match=r"Expected inherited from <class '.+\.BaseMiddleware'>, got <class 'object'>",
        ):
            Messenger(**(kwargs | {"middlewares": [DjangoDatabasePersister(), object()]}))

        # Messaging backend should be inherited from `BaseBackend`
        with pytest.raises(
            TypeError,
            match=r"Expected inherited from <class '.+\.BaseBackend'>, got <class 'object'>",
        ):
            Messenger(**(kwargs | {"messaging_backend": object()}))

    def test_send(self) -> None:
        """Test `.send()` shortcut method, which wraps `.send_request()` for convenience."""
        messenger = Messenger(template_loaders=[], middlewares=[], messaging_backend=_MockBackend())
        with mock.patch.object(messenger, "send_request") as send_request:
            messenger.send(to="channel", template="template", context={"key": "value"}, header={"thread_ts": "123"})
            # ? `send_request.assert_called_once_with` not applicable due to `id_`; unable to mock it
            assert send_request.call_count == 1
            assert cast(MessageRequest, send_request.call_args.kwargs["request"]).model_dump(
                exclude={"id_"},
            ) == MessageRequest(
                template_key="template",
                channel="channel",
                context={"key": "value"},
                header=MessageHeader(thread_ts="123"),
            ).model_dump(exclude={"id_"})

    def test_send_request(self) -> None:
        """Test sending a message request."""
        messenger = Messenger(
            template_loaders=[_MockTemplateLoader({"text": "Hello, {name}!"})],
            middlewares=[_MockMiddleware()],
            messaging_backend=_MockBackend(),
        )
        response = messenger.send_request(request=MessageRequestFactory(context={"name": "Daniel"}))
        assert response
        assert response.model_dump() == {
            "data": {},
            "error": None,
            "ok": True,
            "parent_ts": None,
            "request": {
                "body": {
                    "attachments": None,
                    "blocks": None,
                    "icon_emoji": None,
                    "icon_url": None,
                    "metadata": None,
                    "text": "Hello, Daniel!",
                    "username": None,
                },
                "channel": "some-channel",
                "context": {"name": "Daniel"},
                "header": {
                    "mrkdwn": None,
                    "parse": None,
                    "reply_broadcast": None,
                    "thread_ts": None,
                    "unfurl_links": None,
                    "unfurl_media": None,
                },
                "id_": mock.ANY,
                "template_key": "some-template-key",
            },
            "ts": None,
        }

    def test_send_request_request_middleware_returned_none(self) -> None:
        """When request middleware returned `None`, the request should not be sent."""
        messenger = Messenger(
            template_loaders=[_MockTemplateLoader({"text": "Hello, {name}!"})],
            middlewares=[_MockMiddleware(process_request=lambda _: None)],
            messaging_backend=_MockBackend(),
        )
        response = messenger.send_request(request=MessageRequestFactory())
        assert response is None

    def test_send_request_response_middleware_returned_none(self) -> None:
        """When response middleware returned `None`, it should return the `None`."""
        messenger = Messenger(
            template_loaders=[_MockTemplateLoader({"text": "Hello, {name}!"})],
            middlewares=[_MockMiddleware(process_response=lambda _: None)],
            messaging_backend=_MockBackend(),
        )
        response = messenger.send_request(request=MessageRequestFactory(context={"name": "Daniel"}))
        assert response is None


class _MockTemplateLoader(BaseTemplateLoader):
    def __init__(self, template: Any, *, key: str | None = None) -> None:
        self.template = template
        self.key = key

    def load(self, key: str) -> PythonTemplate | None:
        if self.key and key != self.key:
            return None

        return PythonTemplate(self.template)


class _MockMiddleware(BaseMiddleware):
    def __init__(
        self,
        *,
        process_request: Callable[[MessageRequest], MessageRequest | None] | None = None,
        process_response: Callable[[MessageResponse], MessageResponse | None] | None = None,
    ) -> None:
        self._process_request = process_request
        self._process_response = process_response

    def process_request(self, request: MessageRequest) -> MessageRequest | None:
        if self._process_request:
            return self._process_request(request)

        return super().process_request(request)

    def process_response(self, response: MessageResponse) -> MessageResponse | None:
        if self._process_response:
            return self._process_response(response)

        return super().process_response(response)


class _MockBackend(DummyBackend):
    def __init__(self, *, should_error: bool = False) -> None:
        self.should_error = should_error

    def _send_message(self, *args: Any, **kwargs: Any) -> Any:
        if self.should_error:
            msg = "Some error occurred"
            raise Exception(msg)  # noqa: TRY002

        return super()._send_message(*args, **kwargs)
