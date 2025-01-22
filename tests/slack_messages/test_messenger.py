from typing import Any, cast
from unittest import mock

import pytest

from django_slack_tools.slack_messages.backends import DummyBackend
from django_slack_tools.slack_messages.messenger import Messenger
from django_slack_tools.slack_messages.middlewares import DjangoDatabasePersister, DjangoDatabasePolicyHandler
from django_slack_tools.slack_messages.request import MessageHeader, MessageRequest
from django_slack_tools.slack_messages.template_loaders import DjangoPolicyTemplateLoader, DjangoTemplateLoader


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
            "messaging_backend": DummyBackend(),
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
        messenger = Messenger(template_loaders=[], middlewares=[], messaging_backend=DummyBackend())
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
