import pytest
from django.core.exceptions import ValidationError

from django_slack_bot.utils.dict_template import dict_template_validator, render


# TODO(lasuillard): Test with more complex template
# TODO(lasuillard): Test with lacking or abundant placeholders
def test_render() -> None:
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


def test_dict_template_validator() -> None:
    dict_template_validator(None)
    dict_template_validator({})
    dict_template_validator(
        {
            "message": "{mentions}",
        },
    )
    for value in (
        ["Hello, World"],
        ("Hello, World",),
        "Hello, World",
        12345,
        12345.67890,
    ):
        with pytest.raises(ValidationError):
            dict_template_validator(value)
