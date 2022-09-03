from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwner(BasePermission):
    
    def has_object_permission(self, request, view, obj):
        # если запрос на чтение или это администратор сервиса
        if request.method in SAFE_METHODS or request.user.is_superuser:
            return True
        # остальные мметоды разрешены только владельцу
        if request.method is 'create':
            result = (request.user == obj.user)
        else:
            result = (request.user == obj.creator)
        return result
