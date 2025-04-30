from datetime import datetime, timedelta, timezone
from unittest import mock

import pytest

from django_slack_tools.slack_messages import tasks
from django_slack_tools.slack_messages.models import SlackMessage
from tests.slack_messages.models._factories import SlackMessageFactory


@pytest.mark.django_db
class TestSlackMessage:
    def test_slack_message(self) -> None:
        with mock.patch("django_slack_tools.slack_messages.shortcuts.slack_message") as m:
            tasks.slack_message(
                "test",
                template="simple",
                header={"key": "value"},
                context={"greet": "Hello, world!"},
            )

        m.assert_called_once_with(
            "test",
            template="simple",
            header={"key": "value"},
            context={"greet": "Hello, world!"},
        )


@pytest.mark.usefixtures("celery_worker")
@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
class TestCleanupOldMessages:
    def test_cleanup_old_messages(self) -> None:
        # Arrange
        ts = datetime(2024, 10, 9, 3, 48, 22, tzinfo=timezone.utc)
        _should_deleted = [
            # Should be deleted
            SlackMessageFactory.create(created=ts - timedelta(minutes=6)),
            SlackMessageFactory.create(created=ts - timedelta(minutes=5, seconds=1)),
        ]
        should_remain = [
            # Should not be deleted
            SlackMessageFactory.create(created=ts - timedelta(minutes=5)),
            SlackMessageFactory.create(created=ts - timedelta(minutes=4, seconds=59)),
            SlackMessageFactory.create(created=ts - timedelta(minutes=4)),
        ]

        # Act
        num_deleted = tasks.cleanup_old_messages.delay(base_ts=ts.isoformat(), threshold_seconds=5 * 60).get(timeout=10)

        # Assert
        assert num_deleted == 2
        assert sorted(SlackMessage.objects.values_list("id", flat=True)) == sorted(m.id for m in should_remain)

    def test_cleanup_old_messages_skip_if_threshold_is_none(self) -> None:
        # Arrange
        ts = datetime(2024, 10, 9, 3, 48, 22, tzinfo=timezone.utc)
        SlackMessageFactory(created=ts - timedelta(weeks=4))
        SlackMessageFactory(created=ts - timedelta(hours=1))
        SlackMessageFactory()

        # Act
        num_deleted = tasks.cleanup_old_messages.delay(base_ts=ts.isoformat(), threshold_seconds=None).get(timeout=10)

        # Assert
        assert num_deleted == 0
        assert SlackMessage.objects.count() == 3
