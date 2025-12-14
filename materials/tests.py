from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from materials.models import Course, Lesson
from users.models import User


class LessonTestCase(APITestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(email="admin@example.com")
        self.course = Course.objects.create(name="Python", description="Вводный курс Python", owner=self.user)
        self.lesson = Lesson.objects.create(name="Введение в Python", course=self.course, owner=self.user,
                                            video="https://www.youtube.com/watch?v=34Rp6KVGIEM&list=PLDyJYA6aTY1lPWXBPk0gw6gR8fEtPDGKa")
        self.client.force_authenticate(user=self.user)

    def test_lesson_retrieve(self):
        url = reverse("materials:lesson-get", args=(self.lesson.pk,))
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(
            response.status_code, status.HTTP_200_OK
        )
        self.assertEqual(
            data.get("name"), self.lesson.name
        )

    def test_lesson_create(self):
        url = reverse("materials:lesson-create")
        data = {
            "name": "Основы Django",
            "video": "https://www.youtube.com/watch?v=J84Pit-TN2A"
        }
        response = self.client.post(url, data=data)
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED
        )
        self.assertEqual(
            Lesson.objects.all().count(), 2
        )

    def test_lesson_update(self):
        url = reverse("materials:lesson-update", args=(self.lesson.pk,))
        response = self.client.post(url)
        data = {
            "name": "OOP",
            "video": "https://www.youtube.com/watch?v=q2SGW2VgwAM"
        }
        response = self.client.put(url, data=data)
        data = response.json()
        self.assertEqual(
            response.status_code, status.HTTP_200_OK
        )
        self.assertEqual(
            data.get("name"), "OOP"
        )

    def test_lesson_delete(self):
        url = reverse("materials:lesson-delete", args=(self.lesson.pk,))
        response = self.client.delete(url)
        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT
        )
        self.assertEqual(
            Lesson.objects.all().count(), 0
        )

    def test_lesson_list(self):
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
                    "owner": self.user.pk
                },
            ]
        }
        self.assertEqual(
            response.status_code, status.HTTP_200_OK
        )
        self.assertEqual(
            data, result
        )


class CourseTestCase(APITestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(email="admin@example.com")
        self.course = Course.objects.create(name="Python", description="Вводный курс Python", owner=self.user)
        self.lesson = Lesson.objects.create(name="Введение в Python", course=self.course, owner=self.user,
                                            video="https://www.youtube.com/watch?v=34Rp6KVGIEM&list=PLDyJYA6aTY1lPWXBPk0gw6gR8fEtPDGKa")
        self.client.force_authenticate(user=self.user)

    def test_course_retrieve(self):
        url = reverse("materials:course-detail", args=(self.course.pk,))
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(
            response.status_code, status.HTTP_200_OK
        )
        self.assertEqual(
            data.get("name"), self.course.name
        )

    def test_course_create(self):
        url = reverse("materials:course-list")
        data = {
            "name": "Jawa",
        }
        response = self.client.post(url, data=data)
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED
        )
        self.assertEqual(
            Course.objects.all().count(), 2
        )

    def test_course_update(self):
        url = reverse("materials:course-detail", args=(self.course.pk,))
        response = self.client.post(url)
        data = {
            "name": "Java-разработчик",
        }
        response = self.client.patch(url, data=data)
        data = response.json()
        self.assertEqual(
            response.status_code, status.HTTP_200_OK
        )
        self.assertEqual(
            data.get("name"), "Java-разработчик"
        )

    def test_course_delete(self):
        url = reverse("materials:course-detail", args=(self.course.pk,))
        response = self.client.delete(url)
        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT
        )
        self.assertEqual(
            Course.objects.all().count(), 0
        )

    def test_course_list(self):
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
                    "lessons": [
                        self.lesson.name
                    ],
                    "count_lesson": 1,
                    "subscription": False,
                    "name": self.course.name,
                    "preview": None,
                    "description": self.course.description,
                    "owner": self.user.pk
                },
            ]
        }
        self.assertEqual(
            response.status_code, status.HTTP_200_OK
        )
        self.assertEqual(
            data, result
        )
