import django_filters
from django.contrib.contenttypes.models import ContentType

from materials.models import Course, Lesson

from .models import Payment


class PaymentFilter(django_filters.FilterSet):
    # Фильтрация по дате
    date_after = django_filters.DateFilter(field_name="payment_date", lookup_expr="gte")
    date_before = django_filters.DateFilter(field_name="payment_date", lookup_expr="lte")

    # фильтр по типу объекта: course / lesson
    item_type = django_filters.CharFilter(method="filter_item_type")

    # фильтр по ID объекта (курс или урок)
    item_id = django_filters.NumberFilter(method="filter_item_id")

    class Meta:
        model = Payment
        fields = ["payment_method"]

    def filter_item_type(self, queryset, name, value):
        """
        value = 'course' или 'lesson'
        """
        if value == "course":
            ctype = ContentType.objects.get_for_model(Course)
        elif value == "lesson":
            ctype = ContentType.objects.get_for_model(Lesson)
        else:
            return queryset

        return queryset.filter(content_type=ctype)

    def filter_item_id(self, queryset, name, value):
        return queryset.filter(object_id=value)
