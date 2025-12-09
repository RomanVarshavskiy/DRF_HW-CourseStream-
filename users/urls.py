from django.urls import path
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.apps import UsersConfig
from users.views import (PaymentListAPIView, UserCreateAPIView, UserDestroyAPIView, UserListAPIView,
                         UserRetrieveAPIView, UserUpdateAPIView)

app_name = UsersConfig.name


urlpatterns = [
    path("register/", UserCreateAPIView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(permission_classes=(AllowAny,)), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(permission_classes=(AllowAny,)), name="token_refresh"),
    path("user/", UserListAPIView.as_view(), name="users-list"),
    path("user/<int:pk>/", UserRetrieveAPIView.as_view(), name="user-profile"),
    path("user/<int:pk>/update/", UserUpdateAPIView.as_view(), name="user-update"),
    path("user/<int:pk>/delete/", UserDestroyAPIView.as_view(), name="user-delete"),
    path("payment/", PaymentListAPIView.as_view(), name="payments-list"),
]
