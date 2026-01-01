import requests
from django.db import transaction

from config import settings
from django.utils import timezone
from datetime import timedelta
from materials.models import Course
from celery import shared_task

from materials.tasks import send_information_about_course_update


def send_telegram_message(chat_id, message):
    """Отправка сообщения в Телеграм."""
    params = {
        "chat_id": chat_id,
        "text": message
    }
    requests.get(f'{settings.TELEGRAM_URL}{settings.TELEGRAM_TOKEN}/sendMessage', params=params)

@shared_task
def four_hours_notification():

    courses = Course.objects.filter(notification_pending=True)
    time_now = timezone.now()
    four_hours_ago = time_now - timedelta(hours=4)

    for course in courses:
        with transaction.atomic():
            course = Course.objects.select_for_update().get(id=course.id)

            if not course.notification_pending:
                continue
            if not course.last_notification_at or course.last_notification_at < four_hours_ago:
                send_information_about_course_update.delay(course.id)
                course.last_notification_at = time_now
                course.notification_pending = False
                course.save(update_fields=["last_notification_at", "notification_pending"])



