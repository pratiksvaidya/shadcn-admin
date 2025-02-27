from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.shortcuts import get_object_or_404
from ..models import Document, BusinessDocument, Field, FieldValue, UploadedBusinessDocument
from ..serializers import (
    DocumentSerializer, 
    BusinessDocumentSerializer, 
    FieldSerializer, 
    FieldValueSerializer,
    UploadedBusinessDocumentSerializer
)
from ..services.contact_customer import ContactCustomerService

class DocumentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = DocumentSerializer

    def get_queryset(self):
        return Document.objects.filter(
            Q(agency_owner=self.request.user) |
            Q(is_public=True)
        )

    def perform_create(self, serializer):
        serializer.save(agency_owner=self.request.user)

    @action(detail=True, methods=['get'])
    def businesses(self, request, pk=None):
        """
        Get all businesses that have this document assigned
        """
        document = self.get_object()
        business_documents = BusinessDocument.objects.filter(
            document=document,
            business__customer__agency_owner=request.user
        )
        serializer = BusinessDocumentSerializer(business_documents, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def make_public(self, request, pk=None):
        """
        Make a document public
        """
        document = self.get_object()
        if document.agency_owner != request.user:
            return Response(
                {'error': 'You do not have permission to make this document public'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        document.is_public = True
        document.save()
        serializer = self.get_serializer(document)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def make_private(self, request, pk=None):
        """
        Make a document private
        """
        document = self.get_object()
        if document.agency_owner != request.user:
            return Response(
                {'error': 'You do not have permission to make this document private'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        document.is_public = False
        document.save()
        serializer = self.get_serializer(document)
        return Response(serializer.data)

class BusinessDocumentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = BusinessDocumentSerializer

    def get_queryset(self):
        return BusinessDocument.objects.filter(business__customer__agency_owner=self.request.user)

    @action(detail=True, methods=['post'])
    def call_customer(self, request, pk=None):
        business_document = self.get_object()
        result = ContactCustomerService.call_customer(business_document)
        
        if result['status'] == 'error':
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        return Response(result)

    @action(detail=True, methods=['post'])
    def update_field_values(self, request, pk=None):
        business_document = self.get_object()
        field_values = request.data.get('field_values', [])
        
        updated_values = []
        for field_value in field_values:
            field_id = field_value.get('field_id')
            value = field_value.get('value')
            source = field_value.get('source', 'manual')  # Default to 'manual' if not provided
            
            if not field_id or value is None:
                continue
                
            field = get_object_or_404(Field, id=field_id, document=business_document.document)
            
            obj, created = FieldValue.objects.update_or_create(
                field=field,
                business=business_document.business,
                defaults={
                    'value': value,
                    'source': source
                }
            )
            updated_values.append(obj)
        
        serializer = FieldValueSerializer(updated_values, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        business_document = self.get_object()
        status_value = request.data.get('status')
        
        if not status_value or status_value not in ['pending', 'in_progress', 'completed']:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
            
        business_document.status = status_value
        business_document.save()
        
        serializer = BusinessDocumentSerializer(business_document)
        return Response(serializer.data)

class UploadedBusinessDocumentViewSet(viewsets.ModelViewSet):
    serializer_class = UploadedBusinessDocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UploadedBusinessDocument.objects.filter(business_id=self.kwargs['business_pk'])

    def get_serializer_context(self):
        context = super().get_serializer_context()
        return context

    def perform_create(self, serializer):
        serializer.save(business_id=self.kwargs['business_pk'])

    @action(detail=True, methods=['get'])
    def field_values(self, request, business_pk=None, pk=None):
        uploaded_document = self.get_object()
        field_values = FieldValue.objects.filter(
            business_id=business_pk,
            source='document',
            source_id=uploaded_document.id
        )
        serializer = FieldValueSerializer(field_values, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['put'], url_path='field_values/(?P<field_value_id>[^/.]+)')
    def update_field_value(self, request, business_pk=None, pk=None, field_value_id=None):
        try:
            field_value = FieldValue.objects.get(
                id=field_value_id,
                business_id=business_pk,
                source='document',
                source_id=pk
            )
            field_value.value = request.data.get('value', field_value.value)
            field_value.save()
            serializer = FieldValueSerializer(field_value)
            return Response(serializer.data)
        except FieldValue.DoesNotExist:
            return Response(
                {'error': 'Field value not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['delete'], url_path='field_values/(?P<field_value_id>[^/.]+)')
    def delete_field_value(self, request, business_pk=None, pk=None, field_value_id=None):
        try:
            field_value = FieldValue.objects.get(
                id=field_value_id,
                business_id=business_pk,
                source='document',
                source_id=pk
            )
            field_value.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except FieldValue.DoesNotExist:
            return Response(
                {'error': 'Field value not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

class FieldViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Field.objects.all()
    serializer_class = FieldSerializer
    permission_classes = [permissions.IsAuthenticated]

class FieldValueViewSet(viewsets.ModelViewSet):
    serializer_class = FieldValueSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FieldValue.objects.filter(
            customer__agency_owner=self.request.user
        ) | FieldValue.objects.filter(
            business__customer__agency_owner=self.request.user
        )

    def create(self, request, *args, **kwargs):
        # Check if a field value already exists
        field_id = request.data.get('field')
        customer_id = request.data.get('customer')
        business_id = request.data.get('business')

        existing = FieldValue.objects.filter(
            field_id=field_id,
            customer_id=customer_id,
            business_id=business_id
        ).first()

        if existing:
            # Update existing value
            serializer = self.get_serializer(existing, data=request.data)
        else:
            # Create new value
            serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers) 