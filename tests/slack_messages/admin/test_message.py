from __future__ import annotations

from typing import TYPE_CHECKING, Iterable
from unittest import mock

import pytest
from slack_sdk.errors import SlackApiError

from django_slack_bot.slack_messages.admin import SlackMessageAdmin
from django_slack_bot.slack_messages.models import SlackMessage
from tests._factories import SlackResponseFactory
from tests._helpers import ModelAdminTestBase
from tests.slack_messages.models._factories import SlackMessageFactory

if TYPE_CHECKING:
    from django.test import Client
    from django.test.client import _MonkeyPatchedWSGIResponse


class TestSlackMessageAdmin(ModelAdminTestBase):
    admin_cls = SlackMessageAdmin
    model_cls = SlackMessage
    factory_cls = SlackMessageFactory

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

    @pytest.mark.django_db()
    def test_changelist(self, admin_client: Client) -> None:
        # Test permalink field
        self.factory_cls.create(permalink="https://example.com")
        return super().test_changelist(admin_client)

    @pytest.mark.django_db()
    def test_clone_messages(self, admin_client: Client) -> None:
        # These messages should clone
        messages_to_clone = self.factory_cls.create_batch(size=3)
        ids = [m.id for m in messages_to_clone]

        # Perform action
        response = self._clone_messages(client=admin_client, ids=ids)
        assert response.status_code == 302

        # Check message
        messages = self._get_messages(response.wsgi_request)
        assert messages == ["Cloned 3 messages."]

        # Check messages are cloned
        assert SlackMessage.objects.count() == 6

    @pytest.mark.django_db()
    def test_send_messages(self, admin_client: Client) -> None:
        # These messages should send
        messages_to_send = self.factory_cls.create_batch(size=3)
        ids = [m.id for m in messages_to_send]

        # Perform action
        with mock.patch("slack_bolt.App.client") as m:
            m.chat_postMessage.return_value = SlackResponseFactory(data={"ok": True})
            response = self._send_messages(client=admin_client, ids=ids)

        assert response.status_code == 302

        # Check message
        messages = self._get_messages(response.wsgi_request)
        assert messages == ["Sent 3 messages."]

        # Check messages are sent
        assert SlackMessage.objects.count() == 3
        assert SlackMessage.objects.filter(ok=True).count() == 3

    @pytest.mark.django_db()
    def test_send_messages_partial_failure(self, admin_client: Client) -> None:
        # These messages should send
        messages_to_send = self.factory_cls.create_batch(size=3)
        ids = [m.id for m in messages_to_send]

        # Perform action
        assert SlackMessage.objects.filter(ok=None).count() == 3
        with mock.patch("slack_bolt.App.client") as m:
            m.chat_postMessage.side_effect = [
                SlackResponseFactory(data={"ok": True}),
                SlackApiError("Something went wrong", response=SlackResponseFactory(data={"ok": False})),
                SlackResponseFactory(data={"ok": True}),
            ]
            response = self._send_messages(client=admin_client, ids=ids)

        assert response.status_code == 302

        # Check message
        messages = self._get_messages(response.wsgi_request)
        assert messages == ["Tried to send 3 messages, 2 succeeded and 1 failed."]

        # Check messages are sent
        assert SlackMessage.objects.count() == 3
        assert SlackMessage.objects.filter(ok=True).count() == 2
        assert SlackMessage.objects.filter(ok=False).count() == 1
        assert SlackMessage.objects.filter(ok=None).count() == 0
