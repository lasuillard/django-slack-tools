from datetime import datetime, timedelta, timezone

import pytest

from django_slack_tools.slack_messages.celery import cleanup_old_messages
from django_slack_tools.slack_messages.models import SlackMessage
from tests.slack_messages.models._factories import SlackMessageFactory

pytestmark = pytest.mark.django_db


class TestCleanupOldMessages:
    def test_cleanup_old_messages(self) -> None:
        # Arrange
        ts = datetime(2024, 10, 9, 3, 48, 22, tzinfo=timezone.utc)
        _should_deleted = [
            # Should be deleted
            SlackMessageFactory(created=ts - timedelta(minutes=6)),
            SlackMessageFactory(created=ts - timedelta(minutes=5, seconds=1)),
        ]
        should_remain = [
            # Should not be deleted
            SlackMessageFactory(created=ts - timedelta(minutes=5)),
            SlackMessageFactory(created=ts - timedelta(minutes=4, seconds=59)),
            SlackMessageFactory(created=ts - timedelta(minutes=4)),
        ]

        # Act
        num_deleted = cleanup_old_messages(base_ts=ts.isoformat(), threshold_seconds=5 * 60)  # 5 minutes

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
        num_deleted = cleanup_old_messages(base_ts=ts.isoformat(), threshold_seconds=None)

        # Assert
        assert num_deleted == 0
        assert SlackMessage.objects.count() == 3
