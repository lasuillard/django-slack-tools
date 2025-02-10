from tests.slack_messages._factories import MessageResponseFactory


class TestMessageResponse:
    def test_instance_creation(self) -> None:
        assert MessageResponseFactory()
