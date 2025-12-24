from unittest.mock import patch

from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from materials.models import Course, Lesson, Subscription
from users.models import Payment, User


class UserTestCase(APITestCase):
    """Тесты для API пользователей: создание, получение, обновление, удаление и права доступа."""

    def setUp(self) -> None:
        """Создаёт тестового пользователя и аутентифицирует клиента."""

        self.user = User.objects.create(email="student@example.com")
        self.client.force_authenticate(user=self.user)

    def test_user_retrieve_owner(self):
        """Проверяет, что пользователь может получить свой профиль (PrivateUserSerializer)."""

        url = reverse("users:user-profile", args=(self.user.pk,))
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("email"), self.user.email)

    def test_user_retrieve_other_user_public(self):
        """Проверяет, что пользователь получает публичные данные чужого профиля (PublicUserSerializer)."""

        other_user = User.objects.create(email="other@example.com")

        url = reverse("users:user-profile", args=(other_user.pk,))
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("email"), other_user.email)
        self.assertNotIn("payments", data)

    def test_user_retrieve_unauthenticated(self):
        """Проверяет, что неавторизованный пользователь получает 401 при попытке получить профиль."""

        self.client.force_authenticate(user=None)

        url = reverse("users:user-profile", args=(self.user.pk,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_create(self):
        """Проверяет создание нового пользователя через API."""

        url = reverse("users:register")
        data = {"email": "test@example.com"}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.all().count(), 2)

    def test_user_create_without_email(self):
        """Проверяет валидацию при попытке создать пользователя без email."""

        url = reverse("users:register")
        data = {"email": []}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.all().count(), 1)

    def test_user_update(self):
        """Проверяет, что пользователь может обновить свой профиль."""

        url = reverse("users:user-update", args=(self.user.pk,))
        data = {"phone": "123456789"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()

        self.assertEqual(self.user.phone, "123456789")

    def test_user_update_other_forbidden(self):
        """Проверяет, что пользователь не может обновить чужой профиль (403 Forbidden)."""

        other_user = User.objects.create(email="other@example.com")

        url = reverse("users:user-update", args=(other_user.pk,))
        data = {"phone": "99999999"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_delete(self):
        """Проверяет, что пользователь может удалить свой профиль."""

        url = reverse("users:user-delete", args=(self.user.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.all().count(), 0)

    def test_user_delete_other_forbidden(self):
        """Проверяет, что пользователь не может удалить чужой профиль (403 Forbidden)."""

        other_user = User.objects.create(email="other@example.com")
        url = reverse("users:user-delete", args=(other_user.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_list(self):
        """Проверяет получение списка пользователей через API."""

        url = reverse("users:users-list")
        response = self.client.get(url)
        data = response.json()
        result = [
            {
                "id": self.user.pk,
                "email": self.user.email,
                "phone": self.user.phone,
                "city": self.user.city,
            },
        ]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, result)


class PaymentTestCase(APITestCase):
    """Тесты для API платежей: список платежей и связанные объекты."""

    def setUp(self) -> None:
        """Создаёт двух пользователей, курс и два платежа для тестирования списка."""

        self.user1 = User.objects.create(email="admin@example.com")
        self.user2 = User.objects.create(email="student@example.com")
        self.course = Course.objects.create(name="Python", description="Вводный курс Python", owner=self.user1)
        self.lesson = Lesson.objects.create(
            name="Введение",
            course=self.course,
            owner=self.user1,
            video="https://www.youtube.com/watch?v=test",
        )
        self.course_ct = ContentType.objects.get_for_model(Course)
        self.payment1 = Payment.objects.create(
            payment_method=Payment.PaymentMethod.CASH,
            user=self.user1,
            payment_date="2025-12-01T10:00:00Z",
            amount=100,
            content_type=self.course_ct,
            object_id=self.course.pk,
        )
        self.payment2 = Payment.objects.create(
            payment_method=Payment.PaymentMethod.TRANSFER,
            user=self.user2,
            payment_date="2025-12-02T12:00:00Z",
            amount=200,
            content_type=self.course_ct,
            object_id=self.course.pk,
        )

    def test_payment_list(self):
        """Проверяет, что список платежей возвращается корректно и содержит все созданные записи."""

        self.client.force_authenticate(user=self.user1)

        url = reverse("users:payments-list")
        response = self.client.get(url)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 2)

    @patch("users.views.create_stripe_checkout_session")
    @patch("users.views.create_stripe_price")
    @patch("users.views.convert_rub_to_usd")
    def test_payment_create_success(self, mock_convert, mock_price, mock_session):
        """Проверяет создание нового платежа через API."""

        self.client.force_authenticate(user=self.user1)

        url = reverse("users:payment-create")

        mock_convert.return_value = 50
        mock_price.return_value = {"id": "price_123"}
        mock_session.return_value = ("sess_123", "https://stripe.test/pay")

        data = {
            "amount": 5000,
            "payment_method": "transfer",
            "content_type": "course",
            "object_id": self.course.pk,
        }

        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Payment.objects.count(), 3)

        payment = Payment.objects.latest("id")
        self.assertEqual(payment.user, self.user1)
        self.assertEqual(payment.amount, 5000)
        self.assertEqual(payment.session_id, "sess_123")
        self.assertEqual(payment.link, "https://stripe.test/pay")

    def test_payment_create_unauthenticated(self):
        """Проверяет, что неавторизованный пользователь не может создать платеж."""

        self.client.force_authenticate(user=None)
        url = reverse("users:payment-create")
        data = {
            "amount": 5000,
            "payment_method": "transfer",
            "content_type": "course",
            "object_id": self.course.pk,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch("users.views.create_stripe_checkout_session")
    @patch("users.views.create_stripe_price")
    @patch("users.views.convert_rub_to_usd")
    def test_payment_create_invalid_content_type(self, mock_convert, mock_price, mock_session):
        """Проверяет, что указание некорректного content_type вызывает ValueError."""

        self.client.force_authenticate(user=self.user1)

        url = reverse("users:payment-create")
        mock_convert.return_value = 50
        mock_price.return_value = {"id": "price_123"}
        mock_session.return_value = ("sess_123", "https://stripe.test/pay")

        data = {"amount": 5000, "payment_method": "transfer", "content_type": "invalid", "object_id": 1}

        with self.assertRaises(ValueError):
            self.client.post(url, data=data)


class PaymentStatusTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email="user@example.com")
        self.other_user = User.objects.create(email="other@example.com")
        self.course = Course.objects.create(name="Python", description="Вводный курс Python", owner=self.user)
        self.course_ct = ContentType.objects.get_for_model(Course)

        # Платеж с session_id
        self.payment = Payment.objects.create(
            payment_method=Payment.PaymentMethod.CASH,
            user=self.user,
            amount=100,
            content_type=self.course_ct,
            object_id=self.course.pk,
            session_id="sess_123",
        )

        # Платеж без session_id
        self.payment_no_session = Payment.objects.create(
            payment_method=Payment.PaymentMethod.TRANSFER,
            user=self.user,
            amount=200,
            content_type=self.course_ct,
            object_id=self.course.pk,
            session_id=None,
        )

    @patch("users.views.retrieve_stripe_checkout_session")
    def test_status_success(self, mock_retrieve):
        """Проверка успешного ответа со Stripe."""

        self.client.force_authenticate(user=self.user)
        mock_retrieve.return_value = type(
            "Session", (), {"payment_status": "paid", "amount_total": 1000, "currency": "usd"}
        )()

        url = reverse("users:payment-status", args=[self.payment.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["stripe_status"], "paid")
        self.assertEqual(response.json()["amount_total"], 1000)

    def test_payment_no_session_id(self):
        """Если у платежа нет session_id, возвращается 400."""
        self.client.force_authenticate(user=self.user)
        url = reverse("users:payment-status", args=[self.payment_no_session.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.json())

    def test_payment_not_owner(self):
        """Если пользователь не владелец платежа, возвращается 404."""
        self.client.force_authenticate(user=self.other_user)
        url = reverse("users:payment-status", args=[self.payment.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
