# noqa: D100
from __future__ import annotations

import logging
import re
import xml.etree.ElementTree as ET
from textwrap import dedent
from typing import TYPE_CHECKING, overload

import xmltodict
from django.template import engines

from .base import BaseTemplate

if TYPE_CHECKING:
    from typing import Any

    from django.template.backends.base import BaseEngine

logger = logging.getLogger(__name__)


class DjangoTemplate(BaseTemplate):
    """Template utilizing Django built-in template engine."""

    @overload
    def __init__(self, *, file: str, engine: BaseEngine | None = None) -> None: ...

    @overload
    def __init__(self, *, xml: str, engine: BaseEngine | None = None) -> None: ...

    def __init__(
        self,
        *,
        file: str | None = None,
        xml: str | None = None,
        engine: BaseEngine | None = None,
    ) -> None:
        """Initialize template.

        Args:
            file: Path to file with template.
            xml: XML inline template.
            engine: Template engine to use. Defaults to Django engine.

        Raises:
            ValueError: Some of the arguments are missing or multiple are provided.
        """
        if engine is None:
            engine = engines["django"]

        if sum([1 for value in (file, xml) if value is not None]) != 1:
            msg = "Exactly one of 'xml', or 'file' must be provided."
            raise ValueError(msg)

        if file:
            if file.endswith(".xml"):
                type_ = "xml"
            else:
                msg = "Only XML files are supported."
                raise ValueError(msg)

            template = engine.get_template(file)

        elif xml:
            type_ = "xml"
            template = engine.from_string(xml)

        else:
            # This should unreachable
            msg = "Exactly one of 'xml', or 'file' must be provided."
            raise ValueError(msg)

        self.type_ = type_
        self.template = template
        logger.debug("Template loaded with type: %r, content: %r", type_, template)

    def render(self, *, context: dict[str, Any] | None = None) -> dict:  # noqa: D102
        if context is None:
            context = {}

        string = self.template.render(context=context)
        if self.type_ == "xml":
            obj = _xml_to_dict(string)

        else:
            msg = f"Unsupported template type: {self.type_}"
            raise ValueError(msg)

        return dict(obj)


def _xml_to_dict(xml: str) -> Any:
    """Parse XML string to Python dictionary.

    Following transformations are applied by default:

    - Normalize text nodes: remove single newlines and dedent text, etc.
    - Rename tags for syntactic comfort: block -> blocks, element -> elements

    Please check the tests for more detailed examples.

    Args:
        xml: XML string.

    Returns:
        Parsed dictionary. Be aware, the returned value will be the child of
        top-level node (e.g. <root>...</root>), regardless of its key name.
    """
    xml = _preprocess_xml(xml)
    obj = xmltodict.parse(
        xml,
        attr_prefix="",
        cdata_key="text",
        force_list=("blocks", "elements"),
        postprocessor=_xml_postprocessor,
    )
    return dict(next(iter(obj.values())))


def _preprocess_xml(xml: str) -> str:
    """Normalize XML text nodes."""
    root = ET.fromstring(xml)  # noqa: S314; TODO(lasuillard): Naive belief that XML is safe
    for node in root.iter():
        node.tag = _rename_tag(node.tag)

        if node.tag == "text" and node.text:
            text = dedent(node.text)
            text = _remove_single_newline(text)
            logger.debug("Normalized text node: %r -> %r", node.text, text)
            node.text = text

    return ET.tostring(root, encoding="unicode")


def _rename_tag(tag: str) -> str:
    """Rename tags."""
    if tag == "block":
        return "blocks"

    if tag == "element":
        return "elements"

    return tag


def _remove_single_newline(text: str) -> str:
    """Remove a single newline from repeated newlines. If the are just one newline, replace it with space."""
    return re.sub(r"([\n]+)", lambda m: "\n" * (m.group(1).count("\n") - 1) or " ", text)


def _xml_postprocessor(path: Any, key: str, value: Any) -> tuple[str, Any]:  # noqa: ARG001
    if value == "true":
        return key, True

    if value == "false":
        return key, False

    return key, value
