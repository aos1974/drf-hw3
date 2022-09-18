from django.contrib.auth.models import User
from rest_framework import serializers

from advertisements.models import Advertisement, FavoriteAdvertisement
from api_with_restrictions.settings import MAXIMUM_ADVERTISEMENTS


class UserSerializer(serializers.ModelSerializer):
    """Serializer для пользователя."""

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name',)


class AdvertisementSerializer(serializers.ModelSerializer):
    """Serializer для объявления."""

    creator = UserSerializer(
        read_only=True,
    )

    class Meta:
        model = Advertisement
        fields = ('__all__')

    def create(self, validated_data):
        """Метод для создания"""

        # Простановка значения поля создатель по-умолчанию.
        # Текущий пользователь является создателем объявления
        # изменить или переопределить его через API нельзя.
        # обратите внимание на `context` – он выставляется автоматически
        # через методы ViewSet.
        # само поле при этом объявляется как `read_only=True`

        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, data):
        """Метод для валидации. Вызывается при создании и обновлении."""

        req = self.context.get('request')
        # если это не администратор сервиса
        if not req.user.is_superuser:
            # выполняем проверку на кол-во открытых обьявлений
            queryset = Advertisement.objects.filter(creator_id=req.user.id, draft=False).all()
            cnt = queryset.filter(status='OPEN').count()
            if cnt >= MAXIMUM_ADVERTISEMENTS and data.get('status') is not 'CLOSED':
                raise serializers.ValidationError('Превышено количество открытых объявлений')
        return data


class FavoriteAdvertisementSerializer(serializers.ModelSerializer):
    """Serializer для избранных объявлений."""

    class Meta:
        model = FavoriteAdvertisement
        #fields = ('id', 'user', 'adv_id',)
        fields = ('adv_id',)
        depth = 1

