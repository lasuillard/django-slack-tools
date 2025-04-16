from django_slack_tools.messenger.message_templates import PythonTemplate


class TestPythonTemplate:
    def test_render(self) -> None:
        template = PythonTemplate(
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
