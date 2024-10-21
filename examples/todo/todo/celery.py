import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "todo.settings")

from celery import Celery
from django.conf import settings

app = Celery("todo")

app.conf.broker_url = "redis://localhost:6379/0"

if settings.USE_TZ:
    app.conf.timezone = settings.TIME_ZONE

app.conf.beat_scheduler = "django_celery_beat.schedulers:DatabaseScheduler"
app.conf.beat_schedule = {
    "add-every-30-seconds": {
        "task": "tasks.add",
        "schedule": 30.0,
        "args": (16, 16),
    },
}


# TODO(lasuillard): Just for testing, remove this.
@app.task(name="tasks.add")
def add(x: float, y: float) -> float:  # noqa: D103
    return x + y


app.autodiscover_tasks()
