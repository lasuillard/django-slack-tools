import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "todo.settings")

from celery import Celery
from celery.schedules import crontab
from django.conf import settings

app = Celery("todo")

app.conf.broker_url = "redis://localhost:6379/0"

if settings.USE_TZ:
    app.conf.timezone = settings.TIME_ZONE

app.conf.beat_scheduler = "django_celery_beat.schedulers:DatabaseScheduler"
app.conf.beat_schedule = {
    "Cleanup old Slack messages": {
        "task": "django_slack_tools.slack_messages.tasks.cleanup_old_messages",
        "schedule": crontab(minute=0, hour=4),  # Every 4 AM
        "kwargs": {
            "threshold_seconds": 1 * 24 * 60 * 60,  # Retain for a day
        },
    },
}

app.autodiscover_tasks()
