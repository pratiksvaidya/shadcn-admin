from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from ..models import Business, Document, BusinessDocument, UploadedBusinessDocument
from ..serializers import (
    BusinessSerializer,
    BusinessDetailSerializer,
    BusinessDocumentSerializer,
    UploadedBusinessDocumentSerializer
)
from ..services.document_processor import UploadedDocumentProcessor

class BusinessViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = BusinessSerializer

    def get_queryset(self):
        # Get the agency_id from query params if provided
        agency_id = self.request.query_params.get('agency_id')
        
        # Base queryset - filter businesses where the customer's agency is associated with the current user
        queryset = Business.objects.filter(customer__agency__users=self.request.user)
        
        # If agency_id is provided, further filter by that specific agency
        if agency_id:
            queryset = queryset.filter(customer__agency_id=agency_id)
            
        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BusinessDetailSerializer
        return BusinessSerializer

    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        business = self.get_object()
        business_documents = BusinessDocument.objects.filter(business=business)
        serializer = BusinessDocumentSerializer(business_documents, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_document(self, request, pk=None):
        business = self.get_object()
        document_id = request.data.get('document_id')
        
        if not document_id:
            return Response({'error': 'document_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        document = get_object_or_404(Document, id=document_id)
        
        business_document, created = BusinessDocument.objects.get_or_create(
            business=business,
            document=document,
            defaults={'status': 'pending'}
        )
        
        serializer = BusinessDocumentSerializer(business_document)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def uploaded_documents(self, request, pk=None):
        business = self.get_object()
        uploaded_business_documents = UploadedBusinessDocument.objects.filter(business=business)
        serializer = UploadedBusinessDocumentSerializer(uploaded_business_documents, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def upload_document(self, request, pk=None):
        business = self.get_object()
        file = request.FILES.get('file')
        name = request.data.get('name')
        description = request.data.get('description', '')

        if not file or not name:
            return Response(
                {'error': 'Both file and name are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create the uploaded document
        uploaded_document = UploadedBusinessDocument.objects.create(
            business=business,
            name=name,
            description=description,
            file=file
        )

        # Process the uploaded file
        try:
            processor = UploadedDocumentProcessor(file, business, uploaded_document)
            processor.process()
            
            serializer = UploadedBusinessDocumentSerializer(uploaded_document)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            # If processing fails, delete the uploaded document
            uploaded_document.delete()
            return Response(
                {'error': f'Error processing file: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['delete'], url_path='upload_document/(?P<document_id>[^/.]+)')
    def delete_uploaded_document(self, request, pk=None, document_id=None):
        business = self.get_object()
        try:
            document = UploadedBusinessDocument.objects.get(
                id=document_id,
                business=business
            )
            document.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except UploadedBusinessDocument.DoesNotExist:
            return Response(
                {'error': 'Document not found'}, 
                status=status.HTTP_404_NOT_FOUND
            ) 