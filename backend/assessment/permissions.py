"""Custom Permissions for APIs."""

from rest_framework import permissions


class IsStaffOrReadOnly(permissions.BasePermission):
    """Permission class for allows regulat Users to Read and Staffs to edit."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user and request.user.is_staff