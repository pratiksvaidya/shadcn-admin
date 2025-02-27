from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from ..models import Customer, Business, Document, BusinessDocument, AgencyUser, Agency
from ..serializers import (
    CustomerSerializer,
    BusinessSerializer,
    BusinessDetailSerializer,
    BusinessDocumentSerializer,
    DocumentFieldValuesSerializer
)
from ..services.vapi_service import VapiService

class CustomerViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerSerializer

    def get_queryset(self):
        agency_id = self.request.query_params.get('agency_id')
        if not agency_id:
            raise ValidationError({"agency_id": ["This parameter is required."]})

        # Verify the user has access to this agency
        agency_user = AgencyUser.objects.filter(
            user=self.request.user,
            agency_id=agency_id
        ).first()

        if not agency_user:
            raise ValidationError({"agency_id": ["You do not have access to this agency."]})

        return Customer.objects.filter(agency=agency_user.agency)

    def perform_create(self, serializer):
        agency_id = self.request.data.get('agency_id')
        if not agency_id:
            raise ValidationError({"agency_id": ["This field is required."]})

        # Verify the user has access to this agency
        agency_user = AgencyUser.objects.filter(
            user=self.request.user,
            agency_id=agency_id
        ).first()

        if not agency_user:
            raise ValidationError({"agency_id": ["You do not have access to this agency."]})

        serializer.save(agency=agency_user.agency, created_by=self.request.user)

    @action(detail=True, methods=['get'])
    def businesses(self, request, pk=None):
        """
        Get all businesses associated with this customer
        """
        customer = self.get_object()
        businesses = customer.businesses.all()
        serializer = BusinessSerializer(businesses, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_business(self, request, pk=None):
        """
        Add a new business to this customer
        """
        customer = self.get_object()
        serializer = BusinessSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(customer=customer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        """
        Get all documents associated with this customer's businesses
        """
        customer = self.get_object()
        documents = Document.objects.all()
        data = [
            {
                'document': doc,
                'customer': customer
            }
            for doc in documents
        ]
        serializer = DocumentFieldValuesSerializer(data, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_document_to_business(self, request, pk=None):
        """
        Add a document to a specific business of this customer
        """
        customer = self.get_object()
        business_id = request.data.get('business_id')
        document_id = request.data.get('document_id')
        
        if not business_id or not document_id:
            return Response(
                {'error': 'Both business_id and document_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify the business belongs to this customer
        business = get_object_or_404(Business, id=business_id, customer=customer)
        document = get_object_or_404(Document, id=document_id)
        
        business_document, created = BusinessDocument.objects.get_or_create(
            business=business,
            document=document,
            defaults={'status': 'pending'}
        )
        
        serializer = BusinessDocumentSerializer(business_document)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def vapi_webhook(request):
    """Handle webhook events from VAPI."""
    result = VapiService.process_webhook_event(request.data)
    return Response(
        {
            'status': result['status'],
            'message': result['message']
        },
        status=result['http_status']
    ) 