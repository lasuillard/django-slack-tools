from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from django_slack_tools.slack_messages.admin import SlackMessageAdmin
from django_slack_tools.slack_messages.models import SlackMessage
from tests._helpers import ModelAdminTestBase
from tests.slack_messages.models._factories import SlackMessageFactory

if TYPE_CHECKING:
    from collections.abc import Iterable

    from django.test import Client
    from django.test.client import _MonkeyPatchedWSGIResponse


class TestSlackMessageAdmin(ModelAdminTestBase):
    admin_cls = SlackMessageAdmin
    model_cls = SlackMessage
    factory_cls = SlackMessageFactory

    pytestmark = pytest.mark.django_db()

    def _clone_messages(
        self,
        *,
        client: Client,
        ids: Iterable[SlackMessage],
    ) -> _MonkeyPatchedWSGIResponse:
        return client.post(
            self._reverse("changelist"),
            {
                "action": "_clone_messages",
                "_selected_action": ids,
            },
        )

    def _send_messages(
        self,
        *,
        client: Client,
        ids: Iterable[SlackMessage],
    ) -> _MonkeyPatchedWSGIResponse:
        return client.post(
            self._reverse("changelist"),
            {
                "action": "_send_messages",
                "_selected_action": ids,
            },
        )

    def test_changelist(self, admin_client: Client) -> None:
        # Test permalink field
        self.factory_cls.create(permalink="https://example.com")
        return super().test_changelist(admin_client)
