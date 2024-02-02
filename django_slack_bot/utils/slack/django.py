"""Some stuffs for Django such as field validators."""

from __future__ import annotations

from typing import Any

import pydantic
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .message import MessageBody, MessageHeader


def header_validator(value: Any) -> None:
    """Validate given value is valid message header."""
    try:
        MessageHeader.model_validate(value)
    except pydantic.ValidationError as exc:
        err = _convert_errors(exc)
        raise err from exc


def body_validator(value: Any) -> None:
    """Validate given value is valid message body."""
    try:
        MessageBody.model_validate(value)
    except pydantic.ValidationError as exc:
        err = _convert_errors(exc)
        raise err from exc


def _convert_errors(exc: pydantic.ValidationError) -> ValidationError:
    """Convert Pydantic validation error to Django error."""
    errors = [
        ValidationError(
            _("Input validation failed [msg=%(msg)r, input=%(input)r]"),
            code=", ".join(map(str, err["loc"])),
            params={
                "msg": err["msg"],
                "input": err["input"],
            },
        )
        for err in exc.errors()
    ]
    return ValidationError(errors)
