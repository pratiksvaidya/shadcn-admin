from rest_framework import serializers
from ..models import Document, BusinessDocument, UploadedBusinessDocument
from .field import FieldSerializer, FieldValueSerializer

class DocumentSerializer(serializers.ModelSerializer):
    fields = FieldSerializer(many=True, read_only=True)

    class Meta:
        model = Document
        fields = ['id', 'name', 'description', 'fields', 'created_at', 'updated_at']

class BusinessDocumentSerializer(serializers.ModelSerializer):
    document = DocumentSerializer(read_only=True)
    field_values = serializers.SerializerMethodField()

    class Meta:
        model = BusinessDocument
        fields = ['id', 'business', 'document', 'status', 'field_values', 'created_at', 'updated_at']

    def get_field_values(self, obj):
        # Get field values for this business that correspond to fields in this document
        field_values = obj.business.field_values.filter(field__document=obj.document)
        return FieldValueSerializer(field_values, many=True).data

class DocumentFieldValuesSerializer(serializers.Serializer):
    document = DocumentSerializer()
    field_values = serializers.SerializerMethodField()
    missing_required_fields = serializers.SerializerMethodField()

    def get_field_values(self, obj):
        document = obj['document']
        business = obj.get('business')
        if not business:
            return []
        
        field_values = business.field_values.filter(field__document=document)
        return FieldValueSerializer(field_values, many=True).data

    def get_missing_required_fields(self, obj):
        document = obj['document']
        business = obj.get('business')
        if not business:
            return []

        # Get all required fields for this document
        required_fields = document.fields.filter(is_required=True)

        # Get existing field values
        existing_values = business.field_values.filter(
            field__document=document
        ).values_list('field_id', flat=True)

        # Find missing required fields
        missing_fields = required_fields.exclude(id__in=existing_values)
        return FieldSerializer(missing_fields, many=True).data

class UploadedBusinessDocumentSerializer(serializers.ModelSerializer):
    field_values = serializers.SerializerMethodField()

    class Meta:
        model = UploadedBusinessDocument
        fields = ['id', 'name', 'description', 'file', 'field_values', 'uploaded_at', 'updated_at']
        read_only_fields = ['uploaded_at', 'updated_at']

    def get_field_values(self, obj):
        field_values = obj.business.field_values.filter(
            source='document',
            source_id=obj.id
        )
        return FieldValueSerializer(field_values, many=True).data 