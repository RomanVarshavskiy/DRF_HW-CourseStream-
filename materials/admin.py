from django.contrib import admin

from materials.models import Course, Lesson, Subscription  # название модели


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "description",
    )
    list_filter = ("name",)
    search_fields = ("name",)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "description",
        "course",
    )
    list_filter = ("name",)
    search_fields = ("name",)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "course",
        "created_at",
        "updated_at",
        "is_active",
    )
    list_filter = ("id",)
    search_fields = ("id",)
