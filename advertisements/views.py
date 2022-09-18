from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.throttling import AnonRateThrottle
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from django_filters.rest_framework import DjangoFilterBackend, FilterSet, DateFromToRangeFilter
from advertisements.filters import AdvertisementFilter

from advertisements.models import Advertisement, FavoriteAdvertisement
from advertisements.permissions import IsOwner
from advertisements.serializers import AdvertisementSerializer, FavoriteAdvertisementSerializer
from api_with_restrictions.settings import MAXIMUM_ADVERTISEMENTS


class AdvertisementViewSet(ModelViewSet):
    """ViewSet для объявлений."""

    # TODO: настройте ViewSet, укажите атрибуты для кверисета,
    #   сериализаторов и фильтров

    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filter_backends = [DjangoFilterBackend,]
    filterset_class = AdvertisementFilter
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
        # удалять можно записи с любыми статусами
        if self.action in ['destroy', 'partial_update', 'update']:
            return queryset
        # если это администратор то для него нет ограничений
        if self.request.user.is_superuser:
            return queryset
        # если пользователь не авторизован то ему не показываем черновики
        if self.request.user.id is None:
            queryset = Advertisement.objects.filter(draft=False).all()
        else:
            # для авторизованного пользователя показываем все его объявления
            # и "чистовики" других пользователей
            queryset1 = Advertisement.objects.filter(draft=False).all()
            queryset2 = Advertisement.objects.filter(creator_id=self.request.user.id, draft=True).all()
            queryset = queryset1.union(queryset2, all=True)
        return queryset
 
    def count_status(self, user) -> int:
        cnt = self.queryset.filter(status='OPEN', draft=False).count()
        return cnt
    
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        # только авторизованным пользователям разрешено создавать записи
        if not request.user.is_authenticated:
            return Response({'status' : 'Пользователь не авторизован!'}, 
                                status=status.HTTP_401_UNAUTHORIZED, exception=True)
        return super().create(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        # только авторизованным пользователям разрешено вносить изменения
        if not request.user.is_authenticated:
            return Response({'status' : 'Пользователь не авторизован!'}, 
                                status=status.HTTP_401_UNAUTHORIZED, exception=True)       
        return super().partial_update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        # изменения разрешены только авторизованным пользователям
        if not request.user.is_authenticated:
            return Response({'status' : 'Пользователь не авторизован!'}, 
                                status=status.HTTP_401_UNAUTHORIZED, exception=True)        
        return super().update(request, *args, **kwargs)
    
    # избранные обьявления
    @action(methods=['GET'], detail=False)
    def favorites(self, request):
        queryset = FavoriteAdvertisement.objects.filter(user=request.user.id).all()
        serializer = FavoriteAdvertisementSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(methods=['POST', 'DELETE'], detail=True)
    def favorite(self, request, pk=None):
        if pk is None or request.user.id == None:
            return Response({'status' : f'Nothing to do!'}, 
                            status=status.HTTP_204_NO_CONTENT)
        if request.method == 'POST':
            adv = Advertisement.objects.get(id=pk)
            obj, created = FavoriteAdvertisement.objects.update_or_create(
                    user=request.user, adv_id=adv)
            return Response({'status' : f'Обьяление id=<{pk}> добавлено в избранное'}, 
                            status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            count = FavoriteAdvertisement.objects.filter(
                    user=request.user.id,
                    adv_id=pk).delete()
            return Response({'status' : f'Обьяление id=<{pk}> удалено из избранного'}, 
                            status=status.HTTP_204_NO_CONTENT)
        return Response({'code': 'Ok'})
    
