from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from materials.models import Course, Lesson


class CourseSerializer(ModelSerializer):
    lessons = SerializerMethodField()
    count_lesson = SerializerMethodField()

    def get_lessons(self, course):
        return [lesson.name for lesson in Lesson.objects.filter(course=course)]

    def get_count_lesson(self, course):
        return Lesson.objects.filter(course=course).count()

    class Meta:
        model = Course
        fields = "__all__"


class LessonSerializer(ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"


class LessonDetailSerializer(ModelSerializer):
    course_info = SerializerMethodField()

    def get_course_info(self, obj):
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
