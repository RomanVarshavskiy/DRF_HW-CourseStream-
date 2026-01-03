import logging
from datetime import timedelta

from celery import shared_task
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone

from config.settings import DEFAULT_FROM_EMAIL
from materials.models import Course, Subscription
from materials.services import send_telegram_message

logger = logging.getLogger(__name__)


@shared_task
def send_information_about_course_update(course_id):
    """Отправляет сообщение пользователю об обновлении курса."""
    course = Course.objects.filter(id=course_id).first()
    if not course:
        return

    subscriptions = Subscription.objects.filter(
        course=course,
        is_active=True,
    ).select_related("user")

    message = f"Материалы курса «{course.name}» были обновлены"

    for subscription in subscriptions:
        user = subscription.user
        if not user.email:
            logger.warning(f"User {user.id} has no email")
            continue

        send_mail(
            subject="Обновление курса",
            message=message,
            from_email=DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

        logger.info(f"Email sent to {user.email}")

        if hasattr(user, "tg_chat_id") and user.tg_chat_id:
            send_telegram_message(user.tg_chat_id, message)
            logger.info(f"Telegram message sent to {user.tg_chat_id}")


@shared_task
def four_hours_notification():
    """Отправляет уведомления об обновлении курсов,
    если с момента последнего уведомления прошло более 4 часов."""

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
