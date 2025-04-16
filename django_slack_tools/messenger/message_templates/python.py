# noqa: D100
from __future__ import annotations

import logging
from typing import Any, TypeVar

from .base import BaseTemplate

_PyObj = TypeVar("_PyObj", dict, list, str)

logger = logging.getLogger(__name__)


class PythonTemplate(BaseTemplate[_PyObj]):
    """Template that renders a dictionary."""

    def __init__(self, template: _PyObj) -> None:
        """Initialize the template."""
        self.template = template

    def render(self, context: dict[str, Any]) -> _PyObj:  # noqa: D102
        logger.debug("Rendering template %r with context %r", self.template, context)
        result = _format_obj(self.template, context=context)
        logger.debug("Rendered template %r to %r", self.template, result)
        return result


def _format_obj(obj: _PyObj, *, context: dict[str, Any]) -> _PyObj:
    if isinstance(obj, dict):
        return {key: _format_obj(value, context=context) for key, value in obj.items()}

    if isinstance(obj, list):
        return [_format_obj(item, context=context) for item in obj]

    if isinstance(obj, str):
        return obj.format_map(context)

    return obj
