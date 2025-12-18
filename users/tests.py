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
