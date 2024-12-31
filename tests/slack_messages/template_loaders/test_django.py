import pytest

from django_slack_tools.slack_messages.message_templates import DjangoTemplate, PythonTemplate
from django_slack_tools.slack_messages.models import SlackMessagingPolicy
from django_slack_tools.slack_messages.template_loaders import DjangoPolicyTemplateLoader, DjangoTemplateLoader
from tests.slack_messages.models._factories import SlackMessagingPolicyFactory


class TestDjangoTemplateLoader:
    def test_load(self) -> None:
        loader = DjangoTemplateLoader()
        template = loader.load("greet.xml")
        assert template
        assert isinstance(template, DjangoTemplate)
        assert template.template.template.name == "greet.xml"  # type: ignore[attr-defined] # Maybe false-positive error?


class TestDjangoPolicyTemplateLoader:
    pytestmark = pytest.mark.django_db

    def test_load_python_template(self) -> None:
        policy = SlackMessagingPolicyFactory(
            template_type=SlackMessagingPolicy.TemplateType.DICT,
            template={
                "attachments": [
                    {
                        "blocks": [
                            {"text": {"text": "Hello, World!: {mentions}", "type": "mrkdwn"}, "type": "section"},
                        ],
                        "color": "#f2c744",
                    },
                ],
                "blocks": [{"text": {"text": "Hello, World!: {mentions}", "type": "mrkdwn"}, "type": "section"}],
            },
        )

        loader = DjangoPolicyTemplateLoader()
        template = loader.load(policy.code)

        assert template
        assert isinstance(template, PythonTemplate)
        assert template.template == {
            "attachments": [
                {
                    "blocks": [{"text": {"text": "Hello, World!: {mentions}", "type": "mrkdwn"}, "type": "section"}],
                    "color": "#f2c744",
                },
            ],
            "blocks": [{"text": {"text": "Hello, World!: {mentions}", "type": "mrkdwn"}, "type": "section"}],
        }

    def test_load_django_template_pass_policy_by_code(self) -> None:
        policy = SlackMessagingPolicyFactory(
            template_type=SlackMessagingPolicy.TemplateType.DJANGO,
            template="greet.xml",
        )

        loader = DjangoPolicyTemplateLoader()
        template = loader.load(policy.code)

        assert template
        assert isinstance(template, DjangoTemplate)
        assert template.template.template.name == "greet.xml"  # type: ignore[attr-defined] # Maybe false-positive error?

    def test_load_django_template_pass_policy_by_object(self) -> None:
        """Support passing policy object for convenience."""
        policy = SlackMessagingPolicyFactory(
            template_type=SlackMessagingPolicy.TemplateType.DJANGO,
            template="greet.xml",
        )

        loader = DjangoPolicyTemplateLoader()
        template = loader.load(policy)

        assert template
        assert isinstance(template, DjangoTemplate)
        assert template.template.template.name == "greet.xml"  # type: ignore[attr-defined] # Maybe false-positive error?

    def test_load_django_template_policy_not_found(self) -> None:
        loader = DjangoPolicyTemplateLoader()
        template = loader.load("NOT_FOUND")
        assert template is None

    def test_load_django_inline_template(self) -> None:
        inline_template = """
<root>
    <block type="section">
        <text type="mrkdwn">
            {{ greet }}, {{ mentions }}
        </text>
    </block>
</root>
""".lstrip()
        policy = SlackMessagingPolicyFactory(
            template_type=SlackMessagingPolicy.TemplateType.DJANGO_INLINE,
            template=inline_template,
        )
        loader = DjangoPolicyTemplateLoader()
        template = loader.load(policy.code)

        assert template
        assert isinstance(template, DjangoTemplate)
        assert template.template.template.source == inline_template  # type: ignore[attr-defined] # Maybe false-positive error?

    def test_load_unknown_template_type(self) -> None:
        SlackMessagingPolicyFactory(
            code="TEST",
            template_type=SlackMessagingPolicy.TemplateType.UNKNOWN,
            template="unknown-template",
        )

        loader = DjangoPolicyTemplateLoader()
        with pytest.raises(ValueError, match="Unsupported template type: '?'"):
            loader.load("TEST")
