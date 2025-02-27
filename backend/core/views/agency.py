from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..models import Agency, AgencyUser
from ..serializers.agency import AgencySerializer

class AgencyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A viewset for viewing agencies that the current user has access to.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = AgencySerializer

    def get_queryset(self):
        """
        Get all agencies where the current user is a member.
        """
        return Agency.objects.filter(
            users=self.request.user,
            is_active=True
        ).order_by('name') 