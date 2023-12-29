from django_slack_bot.admin import SlackMessageRecipientAdmin
from django_slack_bot.models import SlackMessageRecipient
from tests.models._factories import SlackMessageRecipientFactory

from ._helpers import ModelAdminTestBase


class TestSlackMessageRecipientAdmin(ModelAdminTestBase):
    admin_cls = SlackMessageRecipientAdmin
    model_cls = SlackMessageRecipient
    factory_cls = SlackMessageRecipientFactory
