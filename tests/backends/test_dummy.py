from django_slack_bot.backends import DummyBackend


class TestDummyBackend:
    def test_backend(self) -> None:
        backend = DummyBackend()
        backend.send_message()
        backend._send_message()
        backend._record_request()
        backend._record_response()
