# noqa: D100
from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from .base import BaseTemplate

if TYPE_CHECKING:
    from typing import Any


import logging

logger = logging.getLogger(__name__)


class DictTemplate(BaseTemplate):
    """Simple dictionary-based template."""

    def __init__(self, template: dict) -> None:
        """Initialize template.

        Args:
            template: Dictionary template.
            kwargs: Keyword arguments passed to template.
        """
        self.template = template

    def render(self, *, context: dict[str, Any] | None = None) -> dict:  # noqa: D102
        context = {} if context is None else context
        result = self.template.copy()
        for k, v in result.items():
            result[k] = _format_obj(v, context=context)

        return result


T = TypeVar("T", dict, list, str)


def _format_obj(obj: T, *, context: dict[str, Any]) -> T:
    """Format object recursively."""
    if isinstance(obj, dict):
        return {k: _format_obj(v, context=context) for k, v in obj.items()}

    if isinstance(obj, str):
        return obj.format_map(context)

    if isinstance(obj, list):
        return [_format_obj(item, context=context) for item in obj]

    return obj
