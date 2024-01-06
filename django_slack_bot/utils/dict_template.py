"""Utils for dictionary-based templates."""
from __future__ import annotations

from typing import Any, TypeVar

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def render(template: dict, **kwargs: Any) -> dict:
    """Render given dictionary template.

    Args:
        template: Dictionary template.
        kwargs: Keyword arguments passed to template.

    Returns:
        Rendered dictionary.
    """
    # Forget the original to format it in-place
    result = template.copy()
    for k, v in result.items():
        result[k] = _format_obj(v, **kwargs)

    return result


def dict_template_validator(value: Any) -> None:
    """Validate given value is valid dictionary template."""
    if value is None:  # No-op template, should work equally to empty dict `{}`
        return

    if not isinstance(value, dict):
        raise ValidationError(
            _("Given object is not a dictionary: %(value)r"),
            params={"value": value},
        )


T = TypeVar("T", dict, list, str)


def _format_obj(obj: T, **kwargs: Any) -> T:
    """Format object recursively."""
    if isinstance(obj, dict):
        return {k: _format_obj(v, **kwargs) for k, v in obj.items()}

    if isinstance(obj, str):
        return obj.format_map(kwargs)

    if isinstance(obj, list):
        return [_format_obj(item, **kwargs) for item in obj]

    return obj
