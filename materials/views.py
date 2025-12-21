from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.generics import (CreateAPIView, DestroyAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView,
                                     get_object_or_404)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from materials.models import Course, Lesson, Subscription
from materials.paginators import CustomPagination
from materials.serializers import CourseSerializer, LessonDetailSerializer, LessonSerializer
from users.permissions import IsModer, IsOwner
from drf_spectacular.utils import extend_schema, OpenApiResponse, extend_schema_view

@extend_schema(tags=["Курсы"])
@extend_schema_view(
    list=extend_schema(description="Список курсов (зависит от роли пользователя)"),
    retrieve=extend_schema(description="Получение детальной информации о курсе"),
    create=extend_schema(description="Создание курса (запрещено модераторам)"),
    update=extend_schema(description="Обновление курса (владелец или модератор)"),
    partial_update=extend_schema(description="Частичное обновление курса"),
    destroy=extend_schema(description="Удаление курса (только владелец)"),
)
class CourseViewSet(ModelViewSet):
    """Управление курсами."""

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        """Назначает владельца курса текущим пользователем."""

        course = serializer.save()
        course.owner = self.request.user
        course.save()

    def get_queryset(self):
        """Возвращает доступные пользователю курсы."""

        if self.request.user.is_superuser or self.request.user.groups.filter(name="moders").exists():
            return Course.objects.all()
        return Course.objects.filter(owner=self.request.user)

    def get_permissions(self):
        """Определяет права доступа в зависимости от действия."""

        if self.action == "create":
            self.permission_classes = (~IsModer,)
        elif self.action in [
            "retrieve",
            "update",
        ]:
            self.permission_classes = (IsModer | IsOwner,)
        elif self.action == "destroy":
            self.permission_classes = (IsOwner,)
        return super().get_permissions()

@extend_schema(
    tags=["Уроки"]
)
class LessonCreateAPIView(CreateAPIView):
    """Создание нового урока."""

    serializer_class = LessonSerializer
    permission_classes = (~IsModer,)

    def perform_create(self, serializer):
        lesson = serializer.save()
        lesson.owner = self.request.user
        lesson.save()

@extend_schema(
    tags=["Уроки"],
    description="Список уроков с учётом прав доступа пользователя"
)
class LessonListAPIView(ListAPIView):
    """Получение списка уроков."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        if self.request.user.is_superuser or self.request.user.groups.filter(name="moders").exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=self.request.user)

@extend_schema(
    tags=["Уроки"]
)
class LessonRetrieveAPIView(RetrieveAPIView):
    """Получение детальной информации об уроке."""

    queryset = Lesson.objects.all()
    serializer_class = LessonDetailSerializer
    permission_classes = (IsModer | IsOwner,)

@extend_schema(
    tags=["Уроки"]
)
class LessonUpdateAPIView(UpdateAPIView):
    """Обновление данных урока."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (IsModer | IsOwner,)

@extend_schema(
    tags=["Уроки"],
    description="Удаление урока (доступно только владельцу)"
)
class LessonDestroyAPIView(DestroyAPIView):
    """Удаление урока."""

    queryset = Lesson.objects.all()
    permission_classes = (~IsModer | IsOwner,)


@extend_schema(
        tags=["Подписки"],
        description="Добавляет или удаляет подписку текущего пользователя на курс.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "course_id": {
                        "type": "integer",
                        "description": "ID курса"
                    }
                },
                "required": ["course_id"],
            }
        },
        responses={
            200: OpenApiResponse(description="Подписка успешно изменена"),
            400: OpenApiResponse(description="course_id не передан"),
            401: OpenApiResponse(description="Пользователь не авторизован"),
            404: OpenApiResponse(description="Курс не найден"),
        },
    )
class SubscriptionAPIView(CreateAPIView):
    """Подписка или отписка пользователя от курса."""
    # permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get("course_id")
        if not course_id:
            return Response({"error": "course_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        course_item = get_object_or_404(Course, id=course_id)

        subs_item = Subscription.objects.filter(user=user, course=course_item)

        # Если подписка у пользователя на этот курс есть - удаляем ее
        if subs_item.exists():
            subs_item.delete()
            message = "подписка удалена"
        # Если подписки у пользователя на этот курс нет - создаем ее
        else:
            Subscription.objects.create(user=user, course=course_item)
            message = "подписка добавлена"
        # Возвращаем ответ в API
        return Response({"message": message}, status=status.HTTP_200_OK)
