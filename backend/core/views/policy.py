from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from ..models import Policy, Business, UploadedBusinessDocument
from ..serializers import PolicySerializer
from ..permissions import HasAgencyAccess

class PolicyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing policies.
    """
    serializer_class = PolicySerializer
    permission_classes = [IsAuthenticated, HasAgencyAccess]

    def get_queryset(self):
        """
        This view should return a list of all policies
        for the currently authenticated user's agency.
        """
        return Policy.objects.filter(
            business__agency__users=self.request.user,
            business__agency__agencyuser__is_active=True
        ).select_related('business').prefetch_related('documents')

    def perform_create(self, serializer):
        """
        Create a new policy and verify the user has access to the business.
        """
        business = get_object_or_404(
            Business.objects.filter(
                agency__users=self.request.user,
                agency__agencyuser__is_active=True
            ),
            pk=self.request.data.get('business')
        )
        serializer.save()

    @action(detail=True, methods=['post'])
    def add_document(self, request, pk=None):
        """
        Add a document to a policy.
        """
        policy = self.get_object()
        document_id = request.data.get('document_id')
        
        if not document_id:
            return Response(
                {'error': 'document_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        document = get_object_or_404(
            UploadedBusinessDocument.objects.filter(
                business__agency__users=request.user,
                business__agency__agencyuser__is_active=True,
                business=policy.business
            ),
            pk=document_id
        )

        policy.documents.add(document)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def remove_document(self, request, pk=None):
        """
        Remove a document from a policy.
        """
        policy = self.get_object()
        document_id = request.data.get('document_id')
        
        if not document_id:
            return Response(
                {'error': 'document_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        document = get_object_or_404(
            policy.documents,
            pk=document_id
        )

        policy.documents.remove(document)
        return Response(status=status.HTTP_204_NO_CONTENT) 