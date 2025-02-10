from django_slack_tools.slack_messages.validators import body_validator, header_validator


def test_header_validator() -> None:
    header_validator({})
    header_validator(
        {
            "mrkdwn": None,
            "parse": None,
            "reply_broadcast": None,
            "thread_ts": None,
            "unfurl_links": None,
            "unfurl_media": None,
        },
    )


def test_body_validator() -> None:
    body_validator({"text": "some-text"})
    body_validator(
        {
            "attachments": None,
            "blocks": None,
            "text": "some-text",
            "icon_emoji": None,
            "icon_url": None,
            "metadata": None,
            "username": None,
        },
    )
