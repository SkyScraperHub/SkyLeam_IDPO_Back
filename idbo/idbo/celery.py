import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "idbo.settings")

app = Celery("idbo")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
app.conf.beat_schedule = {
    'remove_session': {
        'task': 'launcher.tasks.remove_session',
        "schedule": crontab(hour="0", minute="0"),
    },
}