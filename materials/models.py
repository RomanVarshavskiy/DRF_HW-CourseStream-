from django.db import models
from django.db.models import SET_NULL

from users.models import User


class Course(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="name", help_text="Название курса")
    preview = models.ImageField(
        upload_to="materials/preview", blank=True, null=True, verbose_name="preview", help_text="Загрузите картинку"
    )
    description = models.TextField(blank=True, null=True, verbose_name="description", help_text="Укажите описание")
    owner = models.ForeignKey(User, on_delete=SET_NULL, blank=True, null=True, verbose_name="owner")

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def __str__(self):
        return self.name


class Lesson(models.Model):
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
        User, on_delete=SET_NULL, blank=True, null=True, verbose_name="owner", help_text="Укажите владельца"
    )

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"

    def __str__(self):
        return self.name
