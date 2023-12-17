from django_slack_bot.backends import DummyBackend


class TestDummyBackend:
    def test_backend(self) -> None:
        backend = DummyBackend()
        backend.send_message()


# TODO(lasuillard): Do below tests


class TestLoggingBackend:
    pass


class TestSlackBackend:
    pass


class TestSlackRedirectBackend:
    pass
