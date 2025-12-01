from django.urls import path

from users.apps import UsersConfig
from users.views import PaymentListAPIView, UserListAPIView, UserRetrieveUpdateAPIView

app_name = UsersConfig.name


urlpatterns = [
    path("user/", UserListAPIView.as_view(), name="users-list"),
    path("user/<int:pk>/", UserRetrieveUpdateAPIView.as_view(), name="user-profile"),
    path("payment/", PaymentListAPIView.as_view(), name="payments-list"),
]
