from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class User(AbstractUser):
    """Кастомная модель пользователя."""

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


class Payment(models.Model):
    """Модель платежа пользователя."""

    class PaymentMethod(models.TextChoices):
        """Доступные способы оплаты."""

        CASH = "cash", "Cash"
        TRANSFER = "transfer", "Transfer"

    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        verbose_name="Способ оплаты",
    )

    amount = models.PositiveIntegerField(verbose_name="Сумма оплаты", help_text="Укажи сумму оплаты")
    session_id = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Id сессии", help_text="Укажите Id сессии"
    )
    link = models.URLField(
        max_length=500, blank=True, null=True, verbose_name="Ссылка на оплату", help_text="Укажите ссылку на оплату"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Пользователь",
        help_text="Укажите пользователя",
    )
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата оплаты", help_text="Укажи дату оплаты")

    # --- ссылка на Course или Lesson ---
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name="Тип объекта",
        help_text="Тип оплачиваемого объекта (курс или урок)",
    )
    object_id = models.PositiveIntegerField(
        verbose_name="ID объекта",
        help_text="ID курса или урока",
    )
    item = GenericForeignKey("content_type", "object_id")
    stripe_product_id = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Stripe Product ID", help_text="ID продукта в Stripe"
    )
    stripe_price_id = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Stripe Price ID", help_text="ID цены в Stripe"
    )

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"

    def __str__(self):
        return f"Payment by {self.user}  — {self.amount} for {self.item}"
