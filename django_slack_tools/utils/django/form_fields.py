# noqa: D100
from __future__ import annotations

import json
from typing import Any

from django.forms import CharField


class JSONStringField(CharField):
    """Field for JSON field, but for string type specifically."""

    def to_python(self, value: Any) -> str:  # noqa: D102
        return json.dumps(value)
