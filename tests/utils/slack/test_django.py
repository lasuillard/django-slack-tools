import pytest
from django.core.exceptions import ValidationError

from django_slack_tools.slack_messages.validators import body_validator, header_validator


def test_header_validator() -> None:
    header_validator({})
    with pytest.raises(ValidationError, match=".+"):
        header_validator(
            {
                "_unknown_": "Give me an error",
            },
        )


def test_body_validator() -> None:
    body_validator(
        {
            "text": "Hello, World!",
        },
    )
    with pytest.raises(ValidationError, match=".+"):
        body_validator({})
