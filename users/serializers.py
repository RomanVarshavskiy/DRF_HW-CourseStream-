from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from materials.models import Course, Lesson
from users.models import Payment, User


class PaymentSerializer(ModelSerializer):
    """Сериализатор платежа."""

    item = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = (
            "id",
            "payment_method",
            "amount",
            "session_id",
            "link",
            "user",
            "payment_date",
            "item",
        )

    def get_item(self, obj):
        """Возвращает данные связанного объекта (курс или урок)."""

        if isinstance(obj.item, Course):
            return {
                "type": "course",
                "id": obj.item.id,
                "name": obj.item.name,
            }

        if isinstance(obj.item, Lesson):
            return {
                "type": "lesson",
                "id": obj.item.id,
                "name": obj.item.name,
                "course_id": obj.item.course_id,
            }

        return None


class PublicUserSerializer(serializers.ModelSerializer):
    """Публичный сериализатор пользователя."""

    class Meta:
        model = User
        fields = ("id", "email", "phone", "city")


class PrivateUserSerializer(serializers.ModelSerializer):
    """Приватный сериализатор пользователя."""

    payments = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "phone",
            "city",
            "payments",
        )
        read_only_fields = ["email", "payments"]

    def get_payments(self, obj):
        """Возвращает список платежей пользователя."""

        user_payments = obj.payment_set.all()
        return PaymentSerializer(user_payments, many=True).data
