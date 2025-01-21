from typing import Any

import pytest

from django_slack_tools.slack_messages.backends import DummyBackend
from django_slack_tools.slack_messages.messenger import Messenger
from django_slack_tools.slack_messages.middlewares import DjangoDatabasePersister, DjangoDatabasePolicyHandler
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
