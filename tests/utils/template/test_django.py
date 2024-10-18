from __future__ import annotations

import json
from pathlib import Path
from typing import NamedTuple

import pytest

from django_slack_tools.utils.template.django import DjangoTemplate


class _TestCase(NamedTuple):
    xml_input: str
    expect: dict


@pytest.fixture(scope="module")
def testcase(request: pytest.FixtureRequest) -> _TestCase:
    case_dir = Path(__file__).parent / "testcases"
    case_name = str(request.param)
    return _TestCase(
        xml_input=(case_dir / f"{case_name}.xml").read_text(),
        expect=json.loads((case_dir / f"{case_name}.json").read_text()),
    )


class TestDjangoTemplate:
    @pytest.mark.parametrize("testcase", ["001"], indirect=True)
    def test_render_xml_to_json_conversion(self, testcase: _TestCase) -> None:
        actual = DjangoTemplate(xml=testcase.xml_input).render()
        assert actual == testcase.expect
