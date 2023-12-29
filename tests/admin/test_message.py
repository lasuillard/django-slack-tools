from django_slack_bot.admin import SlackMessageAdmin
from django_slack_bot.models import SlackMessage
from tests.models._factories import SlackMessageFactory

from ._helpers import ModelAdminTestBase


class TestSlackMessageAdmin(ModelAdminTestBase):
    admin_cls = SlackMessageAdmin
    model_cls = SlackMessage
    factory_cls = SlackMessageFactory
