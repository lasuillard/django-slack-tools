"""Some stuffs for Django such as field validators."""

from __future__ import annotations

from django.core.exceptions import ValidationError

from .message import MessageBody, MessageHeader


def header_validator(d: dict) -> None:
    """Validate given value is valid message header."""
    try:
        MessageHeader.from_any(d)
    except Exception as exc:
        err = _convert_errors(exc)
        raise err from exc


def body_validator(d: dict) -> None:
    """Validate given value is valid message body."""
    try:
        MessageBody.from_any(d)
    except Exception as exc:
        err = _convert_errors(exc)
        raise err from exc


def _convert_errors(exc: Exception) -> ValidationError:
    return ValidationError(str(exc))
