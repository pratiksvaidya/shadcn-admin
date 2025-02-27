from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from ..models import Policy, Business, UploadedBusinessDocument, AgencyUser
from ..serializers import PolicySerializer, UploadedBusinessDocumentSerializer
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
        # Get the agency_id from the request query parameters
        agency_id = self.request.query_params.get('agency_id')
        
        # Base queryset
        queryset = Policy.objects.select_related('business').prefetch_related('documents')
        
        # Filter by agency_id if provided
        if agency_id:
            # First check if the user has access to this agency
            user_agencies = AgencyUser.objects.filter(
                user=self.request.user,
                agency_id=agency_id
            ).values_list('agency_id', flat=True)
            
            if user_agencies:
                queryset = queryset.filter(
                    business__customer__agency_id=agency_id
                )
            else:
                # If user doesn't have access to the agency, return empty queryset
                return Policy.objects.none()
        else:
            # Get all agencies the user has access to
            user_agencies = AgencyUser.objects.filter(
                user=self.request.user
            ).values_list('agency_id', flat=True)
            
            # Filter policies by these agencies
            queryset = queryset.filter(
                business__customer__agency_id__in=user_agencies
            )
            
        return queryset

    def perform_create(self, serializer):
        """
        Create a new policy and verify the user has access to the business.
        """
        # Get agencies for the user
        user_agencies = AgencyUser.objects.filter(
            user=self.request.user
        ).values_list('agency_id', flat=True)
        
        business = get_object_or_404(
            Business.objects.filter(
                customer__agency_id__in=user_agencies
            ),
            pk=self.request.data.get('business')
        )
        serializer.save()

    @action(detail=True, methods=['post'])
    def add_document(self, request, pk=None):
        """
        Add a document to a policy.
        """
        try:
            policy = self.get_object()
            
            # Check if file is in request.FILES
            if 'file' not in request.FILES:
                return Response({"detail": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
            
            file_obj = request.FILES['file']
            
            # Get optional name and description from form data
            name = request.POST.get('name', '')
            description = request.POST.get('description', '')
            
            # Create the document
            document = UploadedBusinessDocument.objects.create(
                business=policy.business,
                name=name or file_obj.name,
                description=description,
                file=file_obj
            )
            
            # Add the document to the policy
            policy.documents.add(document)
            
            # Return the serialized document
            serializer = UploadedBusinessDocumentSerializer(document)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

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