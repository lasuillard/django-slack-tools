from django_slack_bot.backends import DummyBackend


class DummyBackendTests:
    def test_backend(self) -> None:
        backend = DummyBackend()
        backend.send_message()


# TODO(lasuillard): Do below tests


class LoggingBackendTests:
    pass


class SlackBackendTests:
    pass


class SlackRedirectBackend:
    pass
