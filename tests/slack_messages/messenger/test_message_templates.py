from __future__ import annotations

import json
from pathlib import Path

import pytest
from django.template import TemplateDoesNotExist

from django_slack_tools.slack_messages.messenger import DjangoTemplate


@pytest.fixture(scope="session")
def data_dir() -> Path:
    return Path(__file__).parent / "testcases"


class TestDjangoTemplate:
    def test_instance_creation(self) -> None:
        # Mutually exclusive arguments provided
        with pytest.raises(TypeError, match="Exactly one of 'file' or 'inline' must be provided."):
            DjangoTemplate(file="whatever.xml", inline="<whatever>Whatever</whatever>")  # type: ignore[call-overload]

        # Unsupported file extension
        with pytest.raises(TemplateDoesNotExist, match="template-does-not-exists.xml"):
            DjangoTemplate(file="template-does-not-exists.xml")

    @pytest.mark.parametrize(
        ("xml_input", "json_expect"),
        [
            ("complex-template.xml", "complex-template.json"),
            ("bullet-list.xml", "bullet-list.json"),
            ("approval.xml", "approval.json"),
            ("newsletter.xml", "newsletter.json"),
            ("notification.xml", "notification.json"),
            ("onboarding-1.xml", "onboarding-1.json"),
            ("onboarding-2.xml", "onboarding-2.json"),
            ("poll.xml", "poll.json"),
            ("search-results-1.xml", "search-results-1.json"),
            ("search-results-2.xml", "search-results-2.json"),
        ],
    )
    def test_render(self, xml_input: str, json_expect: str, data_dir: Path) -> None:
        # Arrange
        expect = json.loads((data_dir / json_expect).read_text())

        # Act
        actual = DjangoTemplate(inline=(data_dir / xml_input).read_text()).render({})

        # Assert
        assert actual == expect

    # TODO(lasuillard): Add more tests rendering with context (pick complex templates for test): search-results-1.xml, search-results-2.xml  # noqa: E501
    def test_render_complex_with_context(self, data_dir: Path) -> None:
        # Arrange
        template = DjangoTemplate(file="complex-template-with-context.xml")

        # Act
        context = {
            "restaurants": [
                {
                    "id": "click_me_123",
                    "title": "Farmhouse Thai Cuisine",
                    "rating": 4,
                    "reviews": 1528,
                    "comment": (
                        "They do have some vegan options, like the roti and curry, plus they have a ton of"
                        " salad stuff and noodles can be ordered without meat!! They have something for"
                        " everyone here"
                    ),
                    "image_url": "https://s3-media3.fl.yelpcdn.com/bphoto/c7ed05m9lC2EmA3Aruue7A/o.jpg",
                    "action": {
                        "id": "click_me_123",
                        "display": "Farmhouse",
                        "url": "",
                        "emoji": False,
                    },
                },
                {
                    "id": "click_me_123",
                    "title": "Kin Khao",
                    "rating": 4,
                    "reviews": 1638,
                    "comment": (
                        "The sticky rice also goes wonderfully with the caramelized pork belly, which is"
                        " absolutely melt-in-your-mouth and so soft."
                    ),
                    "image_url": "https://s3-media2.fl.yelpcdn.com/bphoto/korel-1YjNtFtJlMTaC26A/o.jpg",
                    "action": {
                        "id": "click_me_123",
                        "display": "Kin Khao",
                        "url": "https://google.com",
                        "emoji": True,
                    },
                },
                {
                    "title": "Ler Ros",
                    "rating": 4,
                    "reviews": 2082,
                    "comment": (
                        "I would really recommend the Yum Koh Moo Yang - Spicy lime dressing and roasted"
                        " quick marinated pork shoulder, basil leaves, chili & rice powder."
                    ),
                    "image_url": "https://s3-media2.fl.yelpcdn.com/bphoto/DawwNigKJ2ckPeDeDM7jAg/o.jpg",
                    "action": {
                        "id": "click_me_123",
                        "display": "Ler Ros",
                        "url": "https://google.com",
                        "emoji": True,
                    },
                },
            ],
        }
        actual = template.render(context=context)

        # Assert
        expect = json.loads((data_dir / "complex-template.json").read_text())
        assert actual == expect
