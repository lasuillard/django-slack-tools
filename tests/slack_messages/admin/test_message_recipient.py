from __future__ import annotations

from typing import TYPE_CHECKING, Iterable
from unittest import mock

import pytest

from django_slack_bot.slack_messages.admin import SlackMessageRecipientAdmin
from django_slack_bot.slack_messages.admin.message_recipient import _get_channels
from django_slack_bot.slack_messages.models import SlackMessageRecipient
from tests._factories import SlackResponseFactory
from tests._helpers import ModelAdminTestBase
from tests.slack_messages.models._factories import SlackMessageRecipientFactory

if TYPE_CHECKING:
    from django.test import Client
    from django.test.client import _MonkeyPatchedWSGIResponse


_channels = {
    "CHANNEL001": "channel-001",
    "CHANNEL002": "channel-002",
}


class TestSlackMessageRecipientAdmin(ModelAdminTestBase):
    admin_cls = SlackMessageRecipientAdmin
    model_cls = SlackMessageRecipient
    factory_cls = SlackMessageRecipientFactory

    pytestmark = pytest.mark.django_db()

    def _update_channel_names(
        self,
        *,
        client: Client,
        ids: Iterable[SlackMessageRecipient],
    ) -> _MonkeyPatchedWSGIResponse:
        return client.post(
            self._reverse("changelist"),
            {
                "action": "_update_channel_names",
                "_selected_action": ids,
            },
        )

    def test_update_channel_names(self, admin_client: Client) -> None:
        # These recipients should update
        recipients_to_update = [
            self.factory_cls.create(channel="CHANNEL001"),
            self.factory_cls.create(channel="CHANNEL002"),
        ]
        ids = [r.id for r in recipients_to_update]

        # Perform action
        with mock.patch(
            "django_slack_bot.slack_messages.admin.message_recipient._get_channels",
            return_value=_channels,
        ):
            response = self._update_channel_names(client=admin_client, ids=ids)

        assert response.status_code == 302

        # Check message
        messages = self._get_messages(response.wsgi_request)
        assert messages == ["Updated 2 recipients."]

        # Check changes
        recipients = SlackMessageRecipient.objects.filter(id__in=ids)
        assert list(recipients.values("channel", "channel_name")) == [
            {"channel": "CHANNEL001", "channel_name": "#channel-001"},
            {"channel": "CHANNEL002", "channel_name": "#channel-002"},
        ]

    def test_update_channel_names_no_match_for_some(self, admin_client: Client) -> None:
        # These recipients should update
        recipients_to_update = [
            self.factory_cls.create(channel="CHANNEL001"),
            self.factory_cls.create(channel="CHANNEL002"),
            # No match for this
            self.factory_cls.create(channel="CHANNEL003", channel_name="no-channel-for-this"),
        ]
        ids = [r.id for r in recipients_to_update]

        # Perform action
        with mock.patch(
            "django_slack_bot.slack_messages.admin.message_recipient._get_channels",
            return_value=_channels,
        ):
            response = self._update_channel_names(client=admin_client, ids=ids)

        assert response.status_code == 302

        # Check message
        messages = self._get_messages(response.wsgi_request)
        assert messages == [
            "Updated 2 recipients successfully and there were 1 recipients failed to update because no matching data.",
        ]

        # Check changes
        recipients = SlackMessageRecipient.objects.filter(id__in=ids)
        assert list(recipients.values("channel", "channel_name")) == [
            {"channel": "CHANNEL001", "channel_name": "#channel-001"},
            {"channel": "CHANNEL002", "channel_name": "#channel-002"},
            {"channel": "CHANNEL003", "channel_name": "no-channel-for-this"},
        ]


def test_get_channels(mock_slack_client: mock.Mock) -> None:
    mock_slack_client.conversations_list.return_value = SlackResponseFactory(
        data={
            "ok": True,
            "channels": [
                {"id": "CHANNEL001", "name": "channel-001"},
                {"id": "CHANNEL002", "name": "channel-002"},
            ],
        },
    )
    channels = _get_channels()

    assert channels == {"CHANNEL001": "channel-001", "CHANNEL002": "channel-002"}
