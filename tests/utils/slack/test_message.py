import pytest

from django_slack_tools.slack_messages.request import MessageBody, MessageHeader


class TestMessageHeader:
    def test_instance_creation(self) -> None:
        assert MessageHeader()

    def test_from_any(self) -> None:
        assert MessageHeader.from_any(None).as_dict() == {
            "mrkdwn": None,
            "parse": None,
            "reply_broadcast": None,
            "thread_ts": None,
            "unfurl_links": None,
            "unfurl_media": None,
        }
        assert MessageHeader.from_any(
            {"mrkdwn": "some-markdown"},
        ).as_dict() == {
            "mrkdwn": "some-markdown",
            "parse": None,
            "reply_broadcast": None,
            "thread_ts": None,
            "unfurl_links": None,
            "unfurl_media": None,
        }
        with pytest.raises(TypeError, match="Unsupported type <class 'int'>"):
            MessageHeader.from_any(-1)  # type: ignore[arg-type]


class TestMessageBody:
    def test_instance_creation(self) -> None:
        assert MessageBody(text="some-text")

    def test_from_any(self) -> None:
        assert MessageBody.from_any({"text": "some-text"}).as_dict() == {
            "attachments": None,
            "blocks": None,
            "text": "some-text",
            "icon_emoji": None,
            "icon_url": None,
            "metadata": None,
            "username": None,
        }
        assert MessageBody.from_any("some-text").as_dict() == {
            "attachments": None,
            "blocks": None,
            "text": "some-text",
            "icon_emoji": None,
            "icon_url": None,
            "metadata": None,
            "username": None,
        }
        with pytest.raises(TypeError, match="Unsupported type <class 'int'>"):
            MessageBody.from_any(-1)  # type: ignore[arg-type]
