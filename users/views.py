from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiResponse, OpenApiParameter
from rest_framework import filters
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet

from users.models import Payment, User
from users.serializers import PaymentSerializer, PrivateUserSerializer, PublicUserSerializer

from .filters import PaymentFilter
from .permissions import IsSelfOrAdmin

@extend_schema(
    tags=["Пользователи"],
    description="Регистрация нового пользователя",
    responses={201: PublicUserSerializer},
)
class UserCreateAPIView(CreateAPIView):
    """Регистрация пользователя."""

    serializer_class = PublicUserSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        user.set_password(user.password)
        user.save()

@extend_schema(
    tags=["Пользователи"],
    description="Получение списка пользователей",
    responses={200: PublicUserSerializer(many=True)},
)
class UserListAPIView(ListAPIView):
    """Список пользователей."""

    queryset = User.objects.all()
    serializer_class = PublicUserSerializer

@extend_schema(
    tags=["Пользователи"],
)
@extend_schema_view(
    retrieve=extend_schema(
        description=(
            "Получение профиля пользователя. "
            "Владелец видит расширенную информацию, "
            "остальные — публичные данные."
        ),
        responses={
            200: PublicUserSerializer,
            401: OpenApiResponse(description="Неавторизован"),
            404: OpenApiResponse(description="Пользователь не найден"),
        },
    )
)
class UserRetrieveAPIView(RetrieveAPIView):
    """Просмотр профиля пользователя."""

    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.request.user == self.get_object():
            return PrivateUserSerializer
        return PublicUserSerializer


@extend_schema(
    tags=["Пользователи"],
    description="Обновление профиля пользователя (только владелец или администратор)",
    responses={
        200: PrivateUserSerializer,
        403: OpenApiResponse(description="Нет прав доступа"),
    },
)
class UserUpdateAPIView(UpdateAPIView):
    """Обновление профиля пользователя."""

    queryset = User.objects.all()
    serializer_class = PrivateUserSerializer
    permission_classes = (IsSelfOrAdmin,)


@extend_schema(
    tags=["Пользователи"],
    description="Удаление пользователя (только владелец или администратор)",
    responses={
        204: OpenApiResponse(description="Пользователь удалён"),
        403: OpenApiResponse(description="Нет прав доступа"),
    },
)
class UserDestroyAPIView(DestroyAPIView):
    """Удаление пользователя."""

    queryset = User.objects.all()
    permission_classes = (IsSelfOrAdmin,)


@extend_schema(
    tags=["Платежи"],
    description=(
        "Список платежей с возможностью фильтрации "
        "и сортировки по дате оплаты."
    ),
    parameters=[
        OpenApiParameter(
            name="payment_date",
            description="Сортировка по дате оплаты",
            required=False,
            type=str,
        ),
    ],
    responses={200: PaymentSerializer(many=True)},
)
class PaymentListAPIView(ListAPIView):
    """Получение списка платежей."""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = PaymentFilter
    ordering_fields = ("payment_date",)
