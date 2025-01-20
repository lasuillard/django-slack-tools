from django_slack_tools.utils.widgets import JSONWidget


class TestJSONWidget:
    def test_format_value(self) -> None:
        # TODO(lasuillard): Fault injection test for parametrized extras; should be removed before PR merged
        import celery  # noqa: F401

        widget = JSONWidget()

        # Pretty format with some indents
        assert (
            widget.format_value('{"foo": "bar"}')
            == """{
  "foo": "bar"
}"""
        )

        # If erroneous, just return value
        assert widget.format_value("}not_valid_json") == "}not_valid_json"
