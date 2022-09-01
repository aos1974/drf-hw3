from django.contrib import admin

from advertisements.models import Advertisement

# Register your models here.

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'description', 'status', 'creator', 'created_at', 'updated_at']
    list_display_links = ['id', 'title']
    list_filter = ['status', 'creator']
    #search_fields = ['products__title']
    #inlines = [ProductInline,]    
