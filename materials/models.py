from django.db import models

from users.models import User


class Course(models.Model):
    """Модель курса обучения."""

    name = models.CharField(max_length=255, unique=True, verbose_name="name", help_text="Название курса")
    preview = models.ImageField(
        upload_to="materials/preview", blank=True, null=True, verbose_name="preview", help_text="Загрузите картинку"
    )
    description = models.TextField(blank=True, null=True, verbose_name="description", help_text="Укажите описание")
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="owner")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="update_at")
    last_notification_at = models.DateTimeField(blank=True, null=True)
    notification_pending = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def __str__(self):
        return self.name


class Lesson(models.Model):
    """Модель урока. Представляет учебный материал, привязанный к курсу."""

    name = models.CharField(max_length=255, unique=True, verbose_name="name", help_text="Название урока")
    description = models.TextField(blank=True, null=True, verbose_name="description", help_text="Укажите описание")
    preview = models.ImageField(
        upload_to="materials/preview", blank=True, null=True, verbose_name="preview", help_text="Загрузите картинку"
    )
    video = models.URLField(
        max_length=500, blank=True, null=True, verbose_name="video", help_text="Укажите ссылку на видео"
    )
    course = models.ForeignKey(
        Course, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="course", help_text="Укажите курс"
    )
    owner = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="owner", help_text="Укажите владельца"
    )

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"

    def __str__(self):
        return self.name


class Subscription(models.Model):
    """Модель подписки пользователя на курс."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="subscription",
        related_name="subscriptions",
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, blank=True, null=True, verbose_name="course", related_name="subscriptions"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="created_at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="update_at")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("user", "course")
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return f"{self.user} - {self.course}"
