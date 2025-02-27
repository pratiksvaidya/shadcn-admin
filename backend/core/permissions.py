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
                user=request.user
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
        elif hasattr(obj, 'business') and hasattr(obj.business, 'customer'):
            # For Policy objects, the path is business -> customer -> agency
            agency = obj.business.customer.agency
        elif hasattr(obj, 'customer'):
            # For Business objects, the path is customer -> agency
            agency = obj.customer.agency
        else:
            return False

        # Check if user has an association with this agency
        return AgencyUser.objects.filter(
            user=request.user,
            agency=agency
        ).exists() 