from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.throttling import AnonRateThrottle
from rest_framework.response import Response
from rest_framework import status

from django_filters.rest_framework import DjangoFilterBackend, FilterSet, DateFromToRangeFilter

from advertisements.models import Advertisement
from advertisements.permissions import IsOwner
from advertisements.serializers import AdvertisementSerializer
from api_with_restrictions.settings import MAXIMUM_ADVERTISEMENTS

class AdvDateFilter(FilterSet):
    """Фильтр по датам для объявлений"""
    created_at = DateFromToRangeFilter()

    class Meta:
        model = Advertisement
        fields = ['creator', 'created_at', 'draft']


class AdvertisementViewSet(ModelViewSet):
    """ViewSet для объявлений."""

    # TODO: настройте ViewSet, укажите атрибуты для кверисета,
    #   сериализаторов и фильтров

    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filter_backends = [DjangoFilterBackend,]
    filterset_class = AdvDateFilter
    throttle_classes = [AnonRateThrottle]

    def get_permissions(self):
        """Получение прав для действий."""
        # создание, изменение и удаление объектов только для прошедших проверку пользователей
        if self.action in ["create", "update", "partial_update", "destroy"]:
            #return [IsAuthenticated()]
            return [IsOwner()]
        return []

    def get_queryset(self):
        queryset = super().get_queryset()
        # если это администратор то для него нет ограничений
        if self.request.user.is_superuser:
            return queryset
        # если пользователь не авторизован то ему не показываем черновики
        if self.request.user.id is None:
            queryset = Advertisement.objects.filter(draft=False).all()
        else:
            qr = Q(id=self.request.user.id, draft=True)
            queryset = queryset.exclude(qr)
        return queryset
 
    def count_status(self, user) -> int:
        cnt = self.queryset.filter(status='OPEN', draft=False).count()
        return cnt
    
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        # если это не администратор сервиса
        if not request.user.is_superuser:
            # выполняем проверку на кол-во обьявлений
            if self.count_status(request.user) >= MAXIMUM_ADVERTISEMENTS:
                return Response({'status' : 'Превышено количество открытых объявлений'}, 
                                status=status.HTTP_409_CONFLICT, exception=True)
        return super().create(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        # если это не администратор сервиса
        if not request.user.is_superuser:
            # выполняем проверку на кол-во обьявлений        
            if self.count_status(request.user) >= MAXIMUM_ADVERTISEMENTS:
                if request.data.get('status') == 'OPEN' or request.data.get('draft') == False:
                    return Response({'status' : 'Превышено количество открытых объявлений'}, 
                            status=status.HTTP_409_CONFLICT, exception=True)        
        return super().partial_update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        # если это не администратор сервиса
        if not request.user.is_superuser:
            # выполняем проверку на кол-во обьявлений
            if self.count_status(request.user) >= MAXIMUM_ADVERTISEMENTS:
                if request.data.get('status') == 'OPEN' or request.data.get('draft') == False:
                    return Response({'status' : 'Превышено количество открытых объявлений'}, 
                            status=status.HTTP_409_CONFLICT, exception=True)        
        return super().update(request, *args, **kwargs)