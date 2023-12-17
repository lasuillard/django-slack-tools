from django_slack_bot.admin import SlackMessageAdmin
from django_slack_bot.models import SlackMessage
from tests._helpers import ModelAdminTestBase
from tests.models._factories import SlackMessageFactory


class TestSlackMessageAdmin(ModelAdminTestBase):
    admin_cls = SlackMessageAdmin
    model_cls = SlackMessage
    factory_cls = SlackMessageFactory
