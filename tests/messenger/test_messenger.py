from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast
from unittest import mock

import pytest

from django_slack_tools.messenger.shortcuts import MessageHeader, MessageRequest, Messenger, TemplateNotFoundError
from django_slack_tools.slack_messages.messenger import (
    DjangoDatabasePersister,
    DjangoDatabasePolicyHandler,
    DjangoPolicyTemplateLoader,
    DjangoTemplateLoader,
)

from ._factories import MessageRequestFactory
from ._helpers import MockBackend, MockMiddleware, MockTemplate, MockTemplateLoader

if TYPE_CHECKING:
    from django_slack_tools.messenger.shortcuts import MessageResponse


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
            "messaging_backend": MockBackend(),
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
        messenger = Messenger(template_loaders=[], middlewares=[], messaging_backend=MockBackend())
        with mock.patch.object(messenger, "send_request") as send_request:
            messenger.send(to="channel", template="template", context={"key": "value"}, header={"thread_ts": "123"})
            # ? `send_request.assert_called_once_with` not applicable due to `id_`; unable to mock it
            assert send_request.call_count == 1
            assert cast("MessageRequest", send_request.call_args.kwargs["request"]).model_dump(
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
            template_loaders=[MockTemplateLoader()],
            middlewares=[MockMiddleware()],
            messaging_backend=MockBackend(),
        )
        response = messenger.send_request(request=MessageRequestFactory.create(context={"name": "Daniel"}))
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
            template_loaders=[MockTemplateLoader()],
            middlewares=[MockMiddleware(process_request=lambda _: None)],
            messaging_backend=MockBackend(),
        )
        response = messenger.send_request(request=MessageRequestFactory.create())
        assert response is None

    def test_send_request_request_middleware_raised_error(self) -> None:
        """When request middleware raised an error, it should propagate the error."""

        def _throw_error(_: MessageRequest) -> None:
            msg = "Some error occurred"
            raise Exception(msg)  # noqa: TRY002

        messenger = Messenger(
            template_loaders=[MockTemplateLoader()],
            middlewares=[MockMiddleware(process_request=_throw_error)],
            messaging_backend=MockBackend(),
        )
        with pytest.raises(Exception, match="Some error occurred"):
            messenger.send_request(request=MessageRequestFactory.create())

    def test_send_request_template_key_is_not_set(self) -> None:
        """Template key is required to render the message."""
        messenger = Messenger(
            template_loaders=[MockTemplateLoader()],
            middlewares=[MockMiddleware()],
            messaging_backend=MockBackend(),
        )
        with pytest.raises(ValueError, match="Template key is required to render the message"):
            messenger.send_request(request=MessageRequestFactory.create(template_key=None))

    def test_send_request_template_load_not_found(self) -> None:
        """When template is not found, it should raise an error."""
        messenger = Messenger(
            template_loaders=[MockTemplateLoader(key="hacky-key")],
            middlewares=[MockMiddleware()],
            messaging_backend=MockBackend(),
        )
        with pytest.raises(TemplateNotFoundError, match="Template with key 'some-template-key' not found"):
            messenger.send_request(request=MessageRequestFactory.create(template_key="some-template-key"))

    def test_send_request_message_rendering_failed_missing_context_key(self) -> None:
        """Rendering fails if required context key is not provided."""
        messenger = Messenger(
            template_loaders=[MockTemplateLoader()],
            middlewares=[MockMiddleware()],
            messaging_backend=MockBackend(),
        )
        with pytest.raises(KeyError, match="name"):
            messenger.send_request(request=MessageRequestFactory.create(context={}))

    def test_send_request_message_rendering_failed_template_error_propagates_to_caller(self) -> None:
        """Error in rendering propagates to caller."""

        def _throw_error(_: dict[str, Any]) -> Any:
            msg = "Some error occurred"
            raise Exception(msg)  # noqa: TRY002

        messenger = Messenger(
            template_loaders=[MockTemplateLoader(MockTemplate(render=_throw_error))],
            middlewares=[MockMiddleware()],
            messaging_backend=MockBackend(),
        )
        with pytest.raises(Exception, match="Some error occurred"):
            messenger.send_request(request=MessageRequestFactory.create())

    def test_send_request_response_middleware_returned_none(self) -> None:
        """When response middleware returned `None`, it should return the `None`."""
        messenger = Messenger(
            template_loaders=[MockTemplateLoader()],
            middlewares=[MockMiddleware(process_response=lambda _: None)],
            messaging_backend=MockBackend(),
        )
        response = messenger.send_request(request=MessageRequestFactory.create(context={"name": "Daniel"}))
        assert response is None

    def test_send_request_response_middleware_raise_error(self) -> None:
        """When response middleware raised an error, it should propagate the error."""

        def _throw_error(_: MessageResponse) -> None:
            msg = "Some error occurred"
            raise Exception(msg)  # noqa: TRY002

        messenger = Messenger(
            template_loaders=[MockTemplateLoader()],
            middlewares=[MockMiddleware(process_response=_throw_error)],
            messaging_backend=MockBackend(),
        )
        with pytest.raises(Exception, match="Some error occurred"):
            messenger.send_request(request=MessageRequestFactory.create(context={"name": "Daniel"}))
