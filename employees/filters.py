from datetime import timedelta

import django_filters
from django.utils import timezone

from .models import User


class EmployeeFilter(django_filters.FilterSet):
    # Исправляем employeeskill_set на employeeskill
    skill = django_filters.CharFilter(
        field_name="employeeskill__skill__name", lookup_expr="iexact"
    )
    min_experience = django_filters.NumberFilter(method="filter_min_experience")

    class Meta:
        model = User
        fields = ["skill", "min_experience"]

    def filter_min_experience(self, queryset, name, value):
        # Превращаем Decimal в int, чтобы timedelta не ругалась
        days = int(value)
        cutoff_date = timezone.now().date() - timedelta(days=days)
        return queryset.filter(hire_date__lte=cutoff_date)
