from typing import Any, Sequence

import faker
from django.utils import timezone
from factory import Faker, LazyAttribute, post_generation
from factory.django import DjangoModelFactory

from django_slack_bot.models import SlackMention, SlackMessage, SlackMessageRecipient, SlackMessagingPolicy

_fake = faker.Faker()


class SlackMentionFactory(DjangoModelFactory):
    class Meta:
        model = SlackMention

    type = SlackMention.MentionType.UNKNOWN
    name = Faker("name")
    mention_id = Faker("pystr", max_chars=12)


class SlackMessageRecipientFactory(DjangoModelFactory):
    class Meta:
        model = SlackMessageRecipient

    alias = Faker("name")
    channel = Faker("pystr", max_chars=12)
    channel_name = LazyAttribute(lambda _: f"#{_fake.pystr()}")

    @post_generation
    def mentions(
        self: SlackMessageRecipient,
        create: bool,  # noqa: FBT001
        extracted: Sequence[SlackMention],
        **kwargs: Any,  # noqa: ARG002
    ) -> None:
        if not create or not extracted:
            return

        self.mentions.add(*extracted)


class SlackMessageFactory(DjangoModelFactory):
    class Meta:
        model = SlackMessage

    policy = None
    channel = LazyAttribute(lambda _: f"#{_fake.pystr()}")
    header: dict = {}  # noqa: RUF012
    body = LazyAttribute(lambda _: {"text": _fake.paragraph()})
    ok = None
    ts = LazyAttribute(
        # BUG: Sometimes the digit is shorter (e.g. 1702792470.9649)
        lambda _: str(timezone.now().timestamp()),
    )
    parent_ts = ""
    request = None
    response = None


class SlackMessagingPolicyFactory(DjangoModelFactory):
    class Meta:
        model = SlackMessagingPolicy

    code = Faker("pystr")
    enabled = True

    @post_generation
    def recipients(
        self: SlackMessagingPolicy,
        create: bool,  # noqa: FBT001
        extracted: Sequence[SlackMessageRecipient],
        **kwargs: Any,  # noqa: ARG002
    ) -> None:
        if not create or not extracted:
            return

        self.recipients.add(*extracted)

    template = {  # noqa: RUF012
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Hello, World!: {mentions}",
                },
            },
        ],
        "attachments": [
            {
                "color": "#f2c744",
                "blocks": [{"type": "section", "text": {"type": "mrkdwn", "text": "Hello, World!: {mentions}"}}],
            },
        ],
    }
    header_defaults: dict = {}  # noqa: RUF012
