from django_slack_bot.admin import SlackMentionAdmin
from django_slack_bot.models import SlackMention
from tests.models._factories import SlackMentionFactory

from ._helpers import ModelAdminTestBase


class TestSlackMentionAdmin(ModelAdminTestBase):
    admin_cls = SlackMentionAdmin
    model_cls = SlackMention
    factory_cls = SlackMentionFactory
