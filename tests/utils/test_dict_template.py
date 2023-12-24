from django_slack_bot.utils.dict_template import render


class TestDictTemplate:
    def test_render(self) -> None:
        tpl = {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "{greet}",
                    },
                },
            ],
            "unknown": False,
        }
        result = render(tpl, greet="Hello, World!")
        assert result == {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Hello, World!",
                    },
                },
            ],
            "unknown": False,
        }
