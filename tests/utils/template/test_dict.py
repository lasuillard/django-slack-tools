from django_slack_tools.utils.template import DictTemplate


class TestDictTemplate:
    def test_render(self) -> None:
        template = DictTemplate(
            {
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
            },
        )
        result = template.render(context={"greet": "Hello, World!"})
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
