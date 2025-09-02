"""Application settings."""

from __future__ import annotations

from typing import Any, TypedDict, Union

from django.utils.module_loading import import_string
from typing_extensions import NotRequired

LazyInitSpec = TypedDict(
    "LazyInitSpec",
    {
        "class": str,
        "args": NotRequired[tuple],
        "kwargs": NotRequired[dict[str, Any]],
    },
)
LazyInitSupported = Union[LazyInitSpec, str]


def lazy_init(spec: LazyInitSupported) -> Any:
    """Initialize an object from a lazy init spec.

    If string is passed, it is treated as a class import path.
    Otherwise, it is expected to be a dictionary with keys:

    - `class`: class import path,
    - `args`: positional arguments,
    - `kwargs`: keyword arguments.
    """
    if isinstance(spec, str):
        spec = LazyInitSpec({"class": spec})

    class_ = import_string(spec["class"])
    args, kwargs = spec.get("args", ()), spec.get("kwargs", {})
    return class_(*args, **kwargs)
