from factory import Factory
from slack_sdk.web import SlackResponse


class SlackResponseFactory(Factory):
    client = None
    http_verb = "POST"
    api_url = ""
    req_args: dict = {}  # noqa: RUF012
    data: dict = {  # noqa: RUF012
        "ok": True,
    }
    headers: dict = {}  # noqa: RUF012
    status_code = 200

    class Meta:
        model = SlackResponse
