from rest_framework.permissions import BasePermission

class IsAdminRole(BasePermission):
    """
    Custom permission to only allow users with the role 'admin'.
    """
    def has_permission(self, request, view): 
        return request.user and request.user.is_authenticated and getattr(request.user, 'role', None) == 'admin'
