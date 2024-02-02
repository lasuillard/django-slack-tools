import pytest
from django.core.exceptions import ValidationError

from django_slack_tools.utils.slack import body_validator, header_validator


def test_header_validator() -> None:
    header_validator({})
    with pytest.raises(ValidationError):
        header_validator(
            {
                "reply_broadcast": "Give me an error",
            },
        )


def test_body_validator() -> None:
    body_validator(
        {
            "text": "Hello, World!",
        },
    )
    with pytest.raises(ValidationError):
        body_validator({})
