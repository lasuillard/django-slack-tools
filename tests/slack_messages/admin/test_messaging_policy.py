from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from django_slack_tools.slack_messages.admin import SlackMessagingPolicyAdmin
from django_slack_tools.slack_messages.models import SlackMessagingPolicy
from tests._helpers import ModelAdminTestBase
from tests.slack_messages.models._factories import SlackMessagingPolicyFactory

if TYPE_CHECKING:
    from django.test.client import Client


class TestSlackMessagingPolicyAdmin(ModelAdminTestBase):
    admin_cls = SlackMessagingPolicyAdmin
    model_cls = SlackMessagingPolicy
    factory_cls = SlackMessagingPolicyFactory

    @pytest.mark.parametrize(
        argnames="kwargs",
        argvalues=[
            {"template": {"blocks": [{"type": "section", "text": {"type": "plain_text", "text": "Hello"}}]}},
            {"template": {"attachments": [{"type": "section", "text": {"type": "plain_text", "text": "Hello"}}]}},
            {
                "template": {
                    "blocks": [{"type": "section", "text": {"type": "plain_text", "text": "Hello"}}],
                    "attachments": [{"type": "section", "text": {"type": "plain_text", "text": "Hello"}}],
                },
            },
        ],
        ids=["blocks only", "attachments only", "both blocks and attachments"],
    )
    def test_change(self, admin_client: Client, kwargs: dict) -> None:
        obj = self.factory_cls.create(**kwargs)
        url = self._reverse("change", kwargs={"object_id": obj.id})

        # Test visit
        response = admin_client.get(url)
        assert response.status_code == 200
