from celery import shared_task
from celery.utils.log import get_task_logger
from launcher.models import Session
from datetime import timedelta, datetime

logger = get_task_logger(__name__)


@shared_task
def remove_session():
    half_year = datetime.now() - timedelta(days=182)

    Session.objects.filter(date__lte=half_year).delete()
