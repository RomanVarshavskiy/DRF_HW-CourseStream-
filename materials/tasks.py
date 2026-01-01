from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone

from config.settings import DEFAULT_FROM_EMAIL
from materials.models import Course, Subscription
from materials.services import send_telegram_message
import logging

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

#
# @shared_task
# def send_email_about_birthday():
#     """Поздравляет пользователя с днем рождения собаки."""
#     today = timezone.localdate()
#     dogs = Dog.objects.filter(
#         owner__isnull=False,
#         date_born__month=today.month,
#         date_born__day=today.day,
#     )
#
#     if not dogs.exists():
#         logger.info("Сегодня ни у одной собаки нет дня рождения")
#         return
#
#     message = "Поздравляем вашу собаку с днем рождения!"
#     email_list = []
#
#     for dog in dogs:
#         email_list.append(dog.owner.email)
#         if dog.owner.tg_chat_id:
#             send_telegram_message(dog.owner.tg_chat_id, message)
#
#     logger.info(f"Поздравляем {len(email_list)} владельцев")
#
#     if email_list:
#         send_mail(
#             subject="Поздравление 🎉",
#             message=message,
#             from_email=DEFAULT_FROM_EMAIL,
#             recipient_list=email_list,
#         )
