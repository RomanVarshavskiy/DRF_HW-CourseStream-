from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from users.models import User
from users.serializers import UserProfileSerializer


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer

    def get_permissions(self):
        if self.request.method in ("PATCH", "PUT"):
            return [IsAdminUser()]  # редактировать может только админ
        return [IsAuthenticated()]  # а смотреть — любой авторизованный
