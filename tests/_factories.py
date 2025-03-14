from factory import Factory, SubFactory  # type: ignore[attr-defined]
from slack_sdk.errors import SlackApiError
from slack_sdk.web import SlackResponse


class SlackResponseFactory(Factory):
    client = None
    http_verb = "POST"
    api_url = ""
    req_args: dict = {  # noqa: RUF012
        "headers": {},
    }
    data: dict = {  # noqa: RUF012
        "ok": True,
    }
    headers: dict = {}  # noqa: RUF012
    status_code = 200

    class Meta:
        model = SlackResponse


class SlackApiErrorFactory(Factory):
    message = "Something went wrong"
    response = SubFactory(SlackResponseFactory, data={"ok": False})

    class Meta:
        model = SlackApiError
