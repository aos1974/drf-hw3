from django.conf import settings
from django.db import models
 

class AdvertisementStatusChoices(models.TextChoices):
    """Статусы объявления."""

    OPEN = "OPEN", "Открыто"
    CLOSED = "CLOSED", "Закрыто"


class Advertisement(models.Model):
    """Объявление."""

    title = models.TextField()
    description = models.TextField(default='')
    status = models.TextField(
        choices=AdvertisementStatusChoices.choices,
        default=AdvertisementStatusChoices.OPEN
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    draft = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Обьявление'
        verbose_name_plural = 'Обьявления'

    def __str__(self):
        return self.title

# избранные объявления
class FavoriteAdvertisement(models.Model):
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    adv_id = models.ForeignKey(
        Advertisement,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные объявления'
        constraints = [
            models.UniqueConstraint(fields=['user', 'adv_id'], name='unique favorite_adv')
        ]