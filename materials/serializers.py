from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from materials.models import Course, Lesson, Subscription
from materials.validators import validate_link_verification


class CourseSerializer(serializers.ModelSerializer):
    """Сериалайзер курса."""

    lessons = SerializerMethodField()
    count_lesson = SerializerMethodField()
    subscription = SerializerMethodField()

    def get_lessons(self, course):
        """Возвращает список названий уроков курса."""
        return [lesson.name for lesson in Lesson.objects.filter(course=course)]

    def get_count_lesson(self, course):
        """Возвращает количество уроков в курсе."""
        return Lesson.objects.filter(course=course).count()

    def get_subscription(self, course):
        """Проверяет, подписан ли текущий пользователь на курс."""
        request = self.context.get("request")

        if request and request.user.is_authenticated:
            return Subscription.objects.filter(user=request.user, course=course).exists()
        return False

    class Meta:
        model = Course
        fields = "__all__"


class LessonSerializer(serializers.ModelSerializer):
    """Сериалайзер урока."""

    video = serializers.URLField(validators=[validate_link_verification])

    class Meta:
        model = Lesson
        fields = "__all__"


class LessonDetailSerializer(serializers.ModelSerializer):
    """Детальный сериалайзер урока."""

    course_info = SerializerMethodField()

    def get_course_info(self, obj):
        """Возвращает краткую информацию о курсе."""
        if not obj.course:
            return None
        else:
            return {
                "id": obj.course.id,
                "name": obj.course.name,
            }

    class Meta:
        model = Lesson
        fields = ("id", "name", "description", "preview", "video", "course_info")
