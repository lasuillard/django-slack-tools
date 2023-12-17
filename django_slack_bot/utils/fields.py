"""Custom Django fields."""
from __future__ import annotations

from typing import Any

from django.db import models


class SeparatedValuesField(models.TextField):
    """Custom field for storing list of string items.

    Postgres supports `ArrayField` but this field implemented for DBMS-agnostic implementation.
    """

    def __init__(self, *args: Any, separator: str | None = None, **kwargs: Any) -> None:  # noqa: D107
        self.separator = separator or ","
        super().__init__(*args, **kwargs)

    def deconstruct(self) -> Any:  # noqa: D102
        name, path, args, kwargs = super().deconstruct()
        if self.separator != ",":
            kwargs["separator"] = self.separator

        return name, path, args, kwargs

    def from_db_value(self, value: Any, *args: Any, **kwargs: Any) -> Any:  # noqa: ARG002, D102
        return self.to_python(value)

    def to_python(self, value: str | list | None) -> list[str] | None:  # noqa: D102
        if not value:
            return None

        if isinstance(value, list):
            return value

        return value.split(self.separator)

    def get_db_prep_value(self, value: list[str] | None, *args: Any, **kwargs: Any) -> str | None:  # noqa: D102, ARG002
        if not value:
            return None

        return self.separator.join(value)
