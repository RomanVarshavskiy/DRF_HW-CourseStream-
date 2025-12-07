from rest_framework import permissions


class IsModer(permissions.BasePermission):
    """Проверяет, является ли пользователь модератором."""

    message = "Вы не являетесь модератором. У вас не достаточно прав"

    def has_permission(self, request, view):
        return request.user.groups.filter(name="moders").exists()


class IsOwner(permissions.BasePermission):
    """Проверяет, является ли пользователь владельцем."""

    message = "Вы не являетесь владельцем. У вас не достаточно прав"

    def has_object_permission(self, request, view, obj):
        if obj.owner == request.user:
            return True
        return False


class IsSelfOrAdmin(permissions.BasePermission):
    """Разрешает редактировать профиль только самому пользователю или админу."""

    message = "У вас не достаточно прав"

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or request.user == obj
