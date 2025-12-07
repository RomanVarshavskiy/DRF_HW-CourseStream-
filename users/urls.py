from django.urls import path
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny

from users.apps import UsersConfig
from users.views import PaymentListAPIView, UserListAPIView, UserRetrieveUpdateAPIView, UserCreateAPIView, \
    UserDestroyAPIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

app_name = UsersConfig.name


urlpatterns = [
    path("register/", UserCreateAPIView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(permission_classes=(AllowAny,)), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(permission_classes=(AllowAny,)), name="token_refresh"),
    path("user/", UserListAPIView.as_view(), name="users-list"),
    path("user/<int:pk>/", UserRetrieveUpdateAPIView.as_view(), name="user-profile"),
    path("user/<int:pk>/delete/", UserDestroyAPIView.as_view(), name="user-delete"),
    path("payment/", PaymentListAPIView.as_view(), name="payments-list"),
]
