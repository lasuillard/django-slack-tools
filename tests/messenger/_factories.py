from __future__ import annotations

from factory import Factory, LazyAttribute, SubFactory  # type: ignore[attr-defined]

from django_slack_tools.messenger.shortcuts import MessageHeader, MessageRequest, MessageResponse


class MessageRequestFactory(Factory):
    channel = "some-channel"
    template_key = "some-template-key"
    context = {"some": "context"}  # noqa: RUF012
    header = LazyAttribute(lambda _: MessageHeader())

    class Meta:
        model = MessageRequest


class MessageResponseFactory(Factory):
    request = SubFactory(MessageRequestFactory)
    ok = True
    error = None
    data = {"some": "data"}  # noqa: RUF012
    ts = "some-ts"
    parent_ts = None

    class Meta:
        model = MessageResponse
