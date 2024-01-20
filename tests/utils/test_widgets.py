from django_slack_bot.utils.widgets import JSONWidget


class TestJSONWidget:
    def test_format_value(self) -> None:
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
