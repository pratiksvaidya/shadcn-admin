from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from core.models import Policy, Business, UploadedBusinessDocument, AgencyUser
from core.serializers import PolicySerializer, UploadedBusinessDocumentSerializer
from core.permissions import HasAgencyAccess
from core.services.renewal_comparator import RenewalComparator
import json
from datetime import datetime, timedelta


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
        business_id = self.request.query_params.get('business')
        
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
        
        # Filter by business_id if provided
        if business_id:
            queryset = queryset.filter(business_id=business_id)
            
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
    def generate_renewal_comparison(self, request, pk=None):
        """
        Generate a renewal comparison for a policy.
        This endpoint uses the RenewalComparator service to analyze policy documents
        and generate a comparison between the current policy and potential renewal options.
        
        Query Parameters:
            - ai_provider: The AI provider to use ('anthropic' or 'openai'). Default is 'anthropic'.
        """
        try:
            policy = self.get_object()
            
            # Check if policy has documents
            if not policy.documents.exists():
                return Response(
                    {"detail": "No documents available for comparison. Please upload policy documents first."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get AI provider from query parameters (default to anthropic)
            ai_provider = request.query_params.get('ai_provider', 'anthropic').lower()
            
            # Validate AI provider
            if ai_provider not in ['anthropic', 'openai']:
                return Response(
                    {"detail": "Invalid AI provider. Must be either 'anthropic' or 'openai'."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Use the RenewalComparator service with the specified provider
            comparator = RenewalComparator(policy, provider=ai_provider)
            result = comparator.compare()
            
            # Check if there was an error
            if "error" in result:
                return Response({"detail": result["error"]}, status=status.HTTP_400_BAD_REQUEST)
            
            comparison_data = {
                "ai_provider": ai_provider,
                "email": result["email"],
                "attachment": result["attachment"]
            }
            
            return Response(comparison_data, status=status.HTTP_200_OK)
            
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