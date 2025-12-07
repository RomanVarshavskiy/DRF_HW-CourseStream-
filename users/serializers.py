from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from materials.models import Course, Lesson
from users.models import Payment, User


class PaymentSerializer(ModelSerializer):
    item = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = (
            "id",
            "user",
            "payment_date",
            "amount",
            "payment_method",
            "item",
        )

    def get_item(self, obj):
        """Возвращает вложенный объект курса или урока"""
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


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "password", "phone", "city")
        extra_kwargs = {
            "password": {"write_only": True},
        }


class UserProfileSerializer(ModelSerializer):
    payments = serializers.SerializerMethodField()

    def get_payments(self, obj):
        user_payments = obj.payment_set.all()
        return PaymentSerializer(user_payments, many=True).data

    class Meta:
        model = User
        fields = ("id", "email", "phone", "city", "payments",)
        read_only_fields = ["email", "payments"]
