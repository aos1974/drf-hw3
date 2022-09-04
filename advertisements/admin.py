from django.contrib import admin

from advertisements.models import Advertisement, FavoriteAdvertisement

# Register your models here.

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'description', 'status', 'creator', 'created_at', 'updated_at', 'draft']
    list_display_links = ['id', 'title']
    list_filter = ['status', 'creator', 'draft']
    #inlines = [ProductInline,]    

@admin.register(FavoriteAdvertisement)
class FavoriteAdvertisementAdmin(admin.ModelAdmin):
    list_display = ['user','adv_id',]
