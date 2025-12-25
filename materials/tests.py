from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from materials.models import Course, Lesson, Subscription
from users.models import User


class LessonTestCase(APITestCase):
    """Тесты для API уроков: CRUD и права доступа."""

    def setUp(self) -> None:
        """Создаёт пользователя, курс и урок для тестов, аутентифицирует клиента."""

        self.user = User.objects.create(email="admin@example.com")
        self.course = Course.objects.create(name="Python", description="Вводный курс Python", owner=self.user)
        self.lesson = Lesson.objects.create(
            name="Введение в Python",
            course=self.course,
            owner=self.user,
            video="https://www.youtube.com/watch?v=34Rp6KVGIEM&list=PLDyJYA6aTY1lPWXBPk0gw6gR8fEtPDGKa",
        )
        self.client.force_authenticate(user=self.user)

    def test_lesson_retrieve(self):
        """Проверяет получение одного урока по ID."""

        url = reverse("materials:lesson-get", args=(self.lesson.pk,))
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("name"), self.lesson.name)

    def test_lesson_create(self):
        """Проверяет создание нового урока через API."""

        url = reverse("materials:lesson-create")
        data = {"name": "Основы Django", "video": "https://www.youtube.com/watch?v=J84Pit-TN2A"}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.all().count(), 2)

    def test_lesson_update(self):
        """Проверяет обновление урока."""

        url = reverse("materials:lesson-update", args=(self.lesson.pk,))
        response = self.client.post(url)
        data = {"name": "OOP", "video": "https://www.youtube.com/watch?v=q2SGW2VgwAM"}
        response = self.client.put(url, data=data)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("name"), "OOP")

    def test_lesson_delete(self):
        """Проверяет удаление урока."""

        url = reverse("materials:lesson-delete", args=(self.lesson.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.all().count(), 0)

    def test_lesson_list(self):
        """Проверяет получение списка уроков с корректными полями."""

        url = reverse("materials:lessons-list")
        response = self.client.get(url)
        data = response.json()
        result = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": self.lesson.pk,
                    "video": self.lesson.video,
                    "name": self.lesson.name,
                    "description": self.lesson.description,
                    "preview": None,
                    "course": self.course.pk,
                    "owner": self.user.pk,
                },
            ],
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, result)

    def test_lesson_list_by_moders(self):
        """Проверяет, что модератор видит все уроки, включая чужие."""

        student = User.objects.create(email="student@example.com")
        self.lesson = Lesson.objects.create(
            name="Тестирование в Python",
            course=self.course,
            owner=student,
            video="https://www.youtube.com/watch?v=lKo-F3gSl7I",
        )

        moder_user = User.objects.create(email="moder@example.com")
        moder_group = Group.objects.create(name="moders")
        moder_user.groups.add(moder_group)
        self.client.force_authenticate(user=moder_user)

        url = reverse("materials:lessons-list")
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data["results"]), 2)


class CourseTestCase(APITestCase):
    """Тесты для API курсов: CRUD, права доступа и список уроков."""

    def setUp(self) -> None:
        """Создаёт пользователя, курс и урок, аутентифицирует клиента."""

        self.user = User.objects.create(email="admin@example.com")
        self.course = Course.objects.create(name="Python", description="Вводный курс Python", owner=self.user)
        self.lesson = Lesson.objects.create(
            name="Введение в Python",
            course=self.course,
            owner=self.user,
            video="https://www.youtube.com/watch?v=34Rp6KVGIEM&list=PLDyJYA6aTY1lPWXBPk0gw6gR8fEtPDGKa",
        )
        self.client.force_authenticate(user=self.user)

    def test_course_retrieve(self):
        """Проверяет получение курса по ID."""

        url = reverse("materials:course-detail", args=(self.course.pk,))
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("name"), self.course.name)

    def test_course_create(self):
        """Проверяет создание нового курса владельцем."""

        url = reverse("materials:course-list")
        data = {
            "name": "Jawa",
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.all().count(), 2)

    def test_course_create_moder_forbidden(self):
        """Проверяет, что модератор не может создавать курсы (403)."""

        moder_user = User.objects.create(email="moder@example.com")
        moder_group = Group.objects.create(name="moders")
        moder_user.groups.add(moder_group)
        self.client.force_authenticate(user=moder_user)

        url = reverse("materials:course-list")
        data = {
            "name": "Jawa",
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Course.objects.count(), 1)

    def test_course_update(self):
        """Проверяет обновление курса владельцем."""

        url = reverse("materials:course-detail", args=(self.course.pk,))
        data = {
            "name": "Java-разработчик",
        }
        response = self.client.patch(url, data=data)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("name"), "Java-разработчик")

    def test_course_update_not_owner_forbidden(self):
        """Проверяет, что пользователь не-владелец не может обновлять курс."""

        other_user = User.objects.create(email="student@example.com")
        self.client.force_authenticate(user=other_user)

        url = reverse("materials:course-detail", args=(self.course.pk,))
        data = {
            "name": "Java-разработчик",
        }
        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_course_delete(self):
        """Проверяет удаление курса владельцем."""

        url = reverse("materials:course-detail", args=(self.course.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Course.objects.all().count(), 0)

    def test_course_delete_not_owner_forbidden(self):
        """Проверяет, что пользователь не-владелец не может удалить курс."""

        other_user = User.objects.create(email="student@example.com")
        self.client.force_authenticate(user=other_user)

        url = reverse("materials:course-detail", args=(self.course.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_course_list(self):
        """Проверяет получение списка курсов с уроками и дополнительными полями."""

        url = reverse("materials:course-list")
        response = self.client.get(url)
        data = response.json()
        result = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": self.course.pk,
                    "lessons": [self.lesson.name],
                    "count_lesson": 1,
                    "subscription": False,
                    "name": self.course.name,
                    "preview": None,
                    "description": self.course.description,
                    "owner": self.user.pk,
                },
            ],
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, result)

    def test_course_list_by_moders(self):
        """Проверяет, что модератор видит все курсы, включая чужие."""

        student = User.objects.create(email="student@example.com")
        self.course = Course.objects.create(
            name="Тестирование в Python", description="Тестирование в Python", owner=student
        )

        moder_user = User.objects.create(email="moder@example.com")
        moder_group = Group.objects.create(name="moders")
        moder_user.groups.add(moder_group)
        self.client.force_authenticate(user=moder_user)

        url = reverse("materials:course-list")
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data["results"]), 2)


class SubscriptionTestCase(APITestCase):
    """Тесты для API подписок: добавление, удаление и ошибки."""

    def setUp(self):
        """Создаёт пользователя, курс и аутентифицирует клиента."""

        self.user = User.objects.create(email="student@example.com")
        self.course = Course.objects.create(
            name="Python", description="Вводный курс Python", owner=User.objects.create(email="admin@example.com")
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse("materials:subs-create-delete")

    def test_subscription_toggle(self):
        """Проверяет добавление и удаление подписки на курс."""

        # Добавить подписку
        response = self.client.post(self.url, data={"course_id": self.course.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())

        # Удалить подписку
        response = self.client.post(self.url, data={"course_id": self.course.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_subscription_unauthenticated(self):
        """Проверяет, что неавторизованный пользователь получает 401 при подписке."""

        self.client.force_authenticate(user=None)

        response = self.client.post(self.url, data={"course_id": self.course.pk})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_subscription_invalid_course(self):
        """Проверяет, что подписка на несуществующий курс возвращает 404."""

        response = self.client.post(self.url, data={"course_id": 999})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_subscription_without_course_id(self):
        """Проверяет, что отсутствие course_id возвращает 400 с ошибкой."""

        response = self.client.post(self.url, data={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "course_id is required")
