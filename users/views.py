from django.contrib.contenttypes.models import ContentType
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import filters, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import (CreateAPIView, DestroyAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView,
                                     get_object_or_404)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from materials.models import Course, Lesson
from users.models import Payment, User
from users.serializers import PaymentSerializer, PrivateUserSerializer, PublicUserSerializer

from .filters import PaymentFilter
from .permissions import IsSelfOrAdmin
from .services import (convert_rub_to_usd, create_stripe_checkout_session, create_stripe_price,
                       retrieve_stripe_checkout_session, create_stripe_product)


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
    description="Создание нового платежа. Можно привязать к курсу или уроку.",
    request=PaymentSerializer,
    responses={
        201: PaymentSerializer,
        400: "Некорректные данные",
    },
)
class PaymentCreateAPIView(CreateAPIView):
    """Создание нового платежа с возможностью привязки к курсу или уроку."""

    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()

    def perform_create(self, serializer):
        content_type_str = self.request.data.get("content_type")
        object_id = self.request.data.get("object_id")

        content_type = None
        if content_type_str.lower() == "course":
            model = Course
        elif content_type_str.lower() == "lesson":
            model = Lesson
        else:
            raise ValidationError("content_type должен быть 'course' или 'lesson'")

        content_type = ContentType.objects.get_for_model(model)
        item = model.objects.get(pk=object_id)

        payment = serializer.save(
            user=self.request.user,
            content_type=content_type,
            object_id=object_id,
        )
        product = create_stripe_product(item.name)
        amount_in_usd = convert_rub_to_usd(payment.amount)
        price = create_stripe_price(product, amount_in_usd)
        session_id, payment_link = create_stripe_checkout_session(price)
        payment.stripe_product_id = product.id
        payment.stripe_price_id = price.id
        payment.session_id = session_id
        payment.link = payment_link
        payment.save()


@extend_schema(
    tags=["Платежи"],
    description=("Список платежей с возможностью фильтрации " "и сортировки по дате оплаты."),
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


@extend_schema(
    tags=["Платежи"],
    summary="Проверка статуса платежа",
    description=("Возвращает актуальный статус платежа в Stripe по `session_id`. Доступно только владельцу платежа."),
    parameters=[
        OpenApiParameter(
            name="pk",
            type=int,
            location=OpenApiParameter.PATH,
            description="ID платежа",
        ),
    ],
    responses={
        200: OpenApiResponse(description="Статус платежа успешно получен"),
        400: OpenApiResponse(description="У платежа отсутствует session_id"),
        401: OpenApiResponse(description="Пользователь не авторизован"),
        404: OpenApiResponse(description="Платеж не найден или не принадлежит пользователю"),
    },
)
class PaymentStatusAPIView(APIView):
    """Проверка статуса платежа в Stripe по session_id."""

    queryset = Payment.objects.all()
    serializer_class = PrivateUserSerializer

    def get(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk, user=request.user)

        if not payment.session_id:
            return Response({"error": "У платежа нет session_id"}, status=status.HTTP_400_BAD_REQUEST)

        session = retrieve_stripe_checkout_session(payment.session_id)

        return Response(
            {
                "payment_id": payment.id,
                "stripe_status": session.payment_status,
                "amount_total": session.amount_total,
                "currency": session.currency,
            },
            status=status.HTTP_200_OK,
        )
