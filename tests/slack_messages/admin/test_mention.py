from __future__ import annotations

from typing import TYPE_CHECKING, Iterable
from unittest import mock

import pytest

from django_slack_bot.slack_messages.admin import SlackMentionAdmin
from django_slack_bot.slack_messages.admin.mention import _get_mentionable_items
from django_slack_bot.slack_messages.models import SlackMention
from tests._factories import SlackResponseFactory
from tests._helpers import ModelAdminTestBase
from tests.slack_messages.models._factories import SlackMentionFactory

if TYPE_CHECKING:
    from django.test import Client
    from django.test.client import _MonkeyPatchedWSGIResponse

_mentionable_items = {
    "USER001": {"type": SlackMention.MentionType.USER, "name": "Cake"},
    "USER002": {"type": SlackMention.MentionType.USER, "name": "Carrot"},
    "GROUP01": {"type": SlackMention.MentionType.GROUP, "name": "Food"},
}


class TestSlackMentionAdmin(ModelAdminTestBase):
    admin_cls = SlackMentionAdmin
    model_cls = SlackMention
    factory_cls = SlackMentionFactory

    pytestmark = pytest.mark.django_db()

    def _update_mentions(
        self,
        *,
        client: Client,
        ids: Iterable[SlackMention],
    ) -> _MonkeyPatchedWSGIResponse:
        return client.post(
            self._reverse("changelist"),
            {
                "action": "_update_mentions",
                "_selected_action": ids,
            },
        )

    def test_update_mentions(self, admin_client: Client) -> None:
        # These mentions should update
        mentions_to_update = [
            self.factory_cls.create(mention_id="USER001"),
            self.factory_cls.create(mention_id="USER002"),
            self.factory_cls.create(mention_id="GROUP01"),
        ]
        ids = [m.id for m in mentions_to_update]

        # Perform action
        with mock.patch(
            "django_slack_bot.slack_messages.admin.mention._get_mentionable_items",
            return_value=_mentionable_items,
        ):
            response = self._update_mentions(client=admin_client, ids=ids)

        # Check message
        messages = self._get_messages(response.wsgi_request)
        assert messages == ["Updated 3 mentions."]

        # Should update
        mentions = SlackMention.objects.filter(id__in=ids)
        assert list(mentions.values("type", "name")) == [
            {"type": SlackMention.MentionType.USER, "name": "Cake"},
            {"type": SlackMention.MentionType.USER, "name": "Carrot"},
            {"type": SlackMention.MentionType.GROUP, "name": "Food"},
        ]

    def test_update_mentions_no_match_for_some(self, admin_client: Client) -> None:
        # These mentions should update
        mentions_to_update = [
            self.factory_cls.create(mention_id="USER001"),
            self.factory_cls.create(mention_id="GROUP01"),
            # No match for this, so it should leave unchanged
            self.factory_cls.create(type=SlackMention.MentionType.UNKNOWN, mention_id="GROUP02", name="Olive"),
        ]
        ids = [m.id for m in mentions_to_update]

        # Perform action
        with mock.patch(
            "django_slack_bot.slack_messages.admin.mention._get_mentionable_items",
            return_value=_mentionable_items,
        ):
            response = self._update_mentions(client=admin_client, ids=ids)

        assert response.status_code == 302

        # Check message
        messages = self._get_messages(response.wsgi_request)
        assert messages == [
            "Updated 2 mentions successfully and there were 1 mentions failed to update because no matching data.",
        ]

        # Should update
        mentions = SlackMention.objects.filter(id__in=ids)
        assert list(mentions.values("type", "name")) == [
            {"type": SlackMention.MentionType.USER, "name": "Cake"},
            {"type": SlackMention.MentionType.GROUP, "name": "Food"},
            # Should leave unchanged
            {"type": SlackMention.MentionType.UNKNOWN, "name": "Olive"},
        ]

    def test_update_mentions_no_match(self, admin_client: Client) -> None:
        # These mentions should update
        mentions_to_update = [
            self.factory_cls.create(type=SlackMention.MentionType.UNKNOWN, mention_id="🐳"),
            self.factory_cls.create(type=SlackMention.MentionType.UNKNOWN, mention_id="🤖"),
        ]
        ids = [m.id for m in mentions_to_update]

        # Perform action
        with mock.patch(
            "django_slack_bot.slack_messages.admin.mention._get_mentionable_items",
            return_value=_mentionable_items,
        ):
            response = self._update_mentions(client=admin_client, ids=ids)

        assert response.status_code == 302

        # Check message
        messages = self._get_messages(response.wsgi_request)
        assert messages == [
            "Updated 0 mentions successfully and there were 2 mentions failed to update because no matching data.",
        ]

        # Should update
        mentions = SlackMention.objects.filter(id__in=ids)
        assert list(mentions.values("type", "mention_id")) == [
            {"type": SlackMention.MentionType.UNKNOWN, "mention_id": "🐳"},
            {"type": SlackMention.MentionType.UNKNOWN, "mention_id": "🤖"},
        ]


def test_get_mentionable_items(mock_slack_client: mock.Mock) -> None:
    mock_slack_client.users_list.return_value = SlackResponseFactory(
        data={
            "ok": True,
            "members": [
                {"id": "USER001", "profile": {"display_name": "Cake", "real_name": ""}},
                {"id": "USER002", "profile": {"display_name": "", "real_name": "Carrot"}},
            ],
        },
    )
    mock_slack_client.usergroups_list.return_value = SlackResponseFactory(
        data={
            "ok": True,
            "usergroups": [{"id": "GROUP01", "name": "Food"}, {"id": "GROUP02", "name": "Drink"}],
        },
    )
    mentionable_items = _get_mentionable_items()

    assert mentionable_items == {
        "USER001": {
            "type": SlackMention.MentionType.USER,
            "name": "Cake",
        },
        "USER002": {
            "type": SlackMention.MentionType.USER,
            "name": "Carrot",
        },
        "GROUP01": {
            "type": SlackMention.MentionType.GROUP,
            "name": "Food",
        },
        "GROUP02": {
            "type": SlackMention.MentionType.GROUP,
            "name": "Drink",
        },
    }
