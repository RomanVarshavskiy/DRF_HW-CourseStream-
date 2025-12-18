from urllib.parse import urlparse

from rest_framework.serializers import ValidationError

ALLOWED_DOMAINS = ("youtube.com", "www.youtube.com")


def validate_link_verification(value: str):
    domain = urlparse(value).netloc

    if domain not in ALLOWED_DOMAINS:
        raise ValidationError("Запрещено использование ссылок на сторонние ресурсы, кроме youtube.com")
