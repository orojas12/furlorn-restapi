from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        else:
            return obj.user == request.user


class IsSameUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        # obj must be a User instance.
        return obj == request.user
