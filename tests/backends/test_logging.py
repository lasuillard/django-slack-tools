from django_slack_bot.backends import LoggingBackend


class TestLoggingBackend:
    def test_backend(self) -> None:
        backend = LoggingBackend()
        backend.send_message()
        backend._send_message()
        backend._record_request()
        backend._record_response()
