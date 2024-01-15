from __future__ import annotations

from django_slack_bot.slack_messages.admin import SlackMessagingPolicyAdmin
from django_slack_bot.slack_messages.models import SlackMessagingPolicy
from tests._helpers import ModelAdminTestBase
from tests.slack_messages.models._factories import SlackMessagingPolicyFactory


class TestSlackMessagingPolicyAdmin(ModelAdminTestBase):
    admin_cls = SlackMessagingPolicyAdmin
    model_cls = SlackMessagingPolicy
    factory_cls = SlackMessagingPolicyFactory
