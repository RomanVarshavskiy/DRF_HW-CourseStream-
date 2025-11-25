from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
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


class Payments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    payment_date = models.DateTimeField(verbose_name="Дата оплаты", help_text="Укажи дату оплаты")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма оплаты")
    payment_method = models.CharField(
        max_length=20,
        verbose_name="Способ оплаты",
        choices=[
            ("cash", "Cash"),
            ("transfer", "Transfer"),
        ],
    )
    # --- ссылка на Course или Lesson ---
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey("content_type", "object_id")

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"

    def __str__(self):
        return f"Payment by {self.user} for {self.item}"
