# noqa: D100
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

_T = TypeVar("_T")


class BaseTemplate(ABC, Generic[_T]):
    """Base class for templates."""

    template: _T

    @abstractmethod
    def render(self, context: dict[str, Any]) -> Any:
        """Render the template with the given context."""
