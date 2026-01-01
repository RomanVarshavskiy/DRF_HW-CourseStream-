import requests

from config import settings
from users.models import User


def send_telegram_message(chat_id, message):
    """Отправка сообщения в Телеграм."""
    params = {
        "chat_id": chat_id,
        "text": message
    }
    requests.get(f'{settings.TELEGRAM_URL}{settings.TELEGRAM_TOKEN}/sendMessage', params=params)


def deactivate_inactive_users_service(cutoff_date):
    """Деактивирует пользователей, не заходивших в систему дольше заданного срока."""

    return User.objects.filter(
        is_active=True,
        last_login__lt=cutoff_date,
    ).update(is_active=False)
