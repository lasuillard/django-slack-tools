from __future__ import annotations

from django_slack_bot.admin import SlackMessagingPolicyAdmin
from django_slack_bot.models import SlackMessagingPolicy
from tests.models._factories import SlackMessagingPolicyFactory

from ._helpers import ModelAdminTestBase


class TestSlackMessagingPolicyAdmin(ModelAdminTestBase):
    admin_cls = SlackMessagingPolicyAdmin
    model_cls = SlackMessagingPolicy
    factory_cls = SlackMessagingPolicyFactory
