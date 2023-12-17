from django_slack_bot.admin import SlackMessagingPolicyAdmin
from django_slack_bot.models import SlackMessagingPolicy
from tests._helpers import ModelAdminTestBase
from tests.models._factories import SlackMessagingPolicyFactory


class TestSlackMessagingPolicyAdmin(ModelAdminTestBase):
    admin_cls = SlackMessagingPolicyAdmin
    model_cls = SlackMessagingPolicy
    factory_cls = SlackMessagingPolicyFactory
