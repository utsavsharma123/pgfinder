from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerUser(BasePermission):
    """Only PG owner accounts can access."""
    message = 'Only PG owners can perform this action.'

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'owner'


class IsListingOwner(BasePermission):
    """Only the owner of the specific listing can modify it."""
    message = 'You do not own this listing.'

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'owner'

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.owner == request.user
