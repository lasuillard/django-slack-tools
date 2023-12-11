"""Validators for handy."""
from __future__ import annotations

from typing import Any

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def dict_template_validator(value: Any) -> None:
    """Validate given value is valid dictionary template."""
    if value is None:  # No-op template, should work equally to empty dict `{}`
        pass

    if not isinstance(value, dict):
        raise ValidationError(
            _("Given object is not dictionary"),
            params={"value": value},
        )
