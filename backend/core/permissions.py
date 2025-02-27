from rest_framework import permissions
from .models import Agency, AgencyUser

class HasAgencyAccess(permissions.BasePermission):
    """
    Custom permission to only allow users with active agency access.
    """

    def has_permission(self, request, view):
        # Allow all authenticated users to list and retrieve
        if not request.user or not request.user.is_authenticated:
            return False

        # For create, update, delete actions, check if user has an active agency association
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return AgencyUser.objects.filter(
                user=request.user,
                is_active=True
            ).exists()

        return True

    def has_object_permission(self, request, view, obj):
        # Allow read access if user is in the same agency
        if not request.user or not request.user.is_authenticated:
            return False

        # Get the agency from the object
        # Different models will have different paths to their agency
        if hasattr(obj, 'agency'):
            agency = obj.agency
        elif hasattr(obj, 'business'):
            agency = obj.business.agency
        else:
            return False

        # Check if user has an active association with this agency
        return AgencyUser.objects.filter(
            user=request.user,
            agency=agency,
            is_active=True
        ).exists() 