# noqa: D100
from __future__ import annotations

from typing import Any


def make_repr(obj: Any) -> str:
    """Make a repr string for an object."""
    args = ", ".join(f"{k}={v!r}" for k, v in obj.__dict__.items())
    return f"{obj.__class__.__name__}({args})"
