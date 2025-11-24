from rest_framework.serializers import ModelSerializer

from users.models import User


class UserProfileSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

        read_only_fields = ["email"]
