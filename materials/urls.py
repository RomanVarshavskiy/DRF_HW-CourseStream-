from django.urls import path
from rest_framework.routers import SimpleRouter

from materials.apps import MaterialsConfig
from materials.views import (CourseViewSet, LessonCreateAPIView, LessonDestroyAPIView, LessonListAPIView,
                             LessonRetrieveAPIView, LessonUpdateAPIView, SubscriptionAPIView)

app_name = MaterialsConfig.name

router = SimpleRouter()
router.register("", CourseViewSet)


urlpatterns = [
    path("lesson/", LessonListAPIView.as_view(), name="lessons-list"),
    path("lesson/<int:pk>/", LessonRetrieveAPIView.as_view(), name="lesson-get"),
    path("lesson/<int:pk>/update/", LessonUpdateAPIView.as_view(), name="lesson-update"),
    path("lesson/<int:pk>/delete/", LessonDestroyAPIView.as_view(), name="lesson-delete"),
    path("lesson/create/", LessonCreateAPIView.as_view(), name="lesson-create"),
    path("subscription/", SubscriptionAPIView.as_view(), name="subs-create-delete"),
]

urlpatterns += router.urls
