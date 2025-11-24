from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models


class User(AbstractBaseUser):
    username = None

    email = models.EmailField(unique=True, verbose_name="email", help_text="Email address")

    phone = models.CharField(max_length=11, blank=True, null=True, verbose_name="phone", help_text="Phone number")
    city = models.CharField(max_length=255, blank=True, null=True, verbose_name="city", help_text="City")
    avatar = models.ImageField(
        upload_to="users/avatars", blank=True, null=True, verbose_name="avatar", help_text="Avatar"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email
