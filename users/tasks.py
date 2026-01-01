import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from users.services import deactivate_inactive_users_service

logger = logging.getLogger(__name__)


@shared_task
def deactivate_inactive_users():
    """Деактивирует пользователей, не входивших в систему более 30 дней."""

    cutoff_date = timezone.now() - timedelta(days=30)
    deactivated_users = deactivate_inactive_users_service(cutoff_date)
    logger.info(f"Деактивировано {deactivated_users} пользователей")
    return deactivated_users
