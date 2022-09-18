from django_filters import rest_framework as filters
from django_filters.rest_framework import DateFromToRangeFilter
from advertisements.models import Advertisement


class AdvertisementFilter(filters.FilterSet):
    """Фильтры для объявлений."""

    created_at = DateFromToRangeFilter()

    class Meta:
        model = Advertisement
        fields = ['creator', 'created_at', 'draft', 'status']
 