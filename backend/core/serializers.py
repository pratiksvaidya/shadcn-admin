from rest_framework import serializers
from .models import Customer, Business, Document, Field, FieldValue, BusinessDocument, UploadedBusinessDocument
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ['id', 'name', 'description', 'address', 'phone_number', 'email', 'customer', 'created_at', 'updated_at']

class CustomerSerializer(serializers.ModelSerializer):
    businesses = BusinessSerializer(many=True, read_only=True)

    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number', 'businesses', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['agency_owner'] = self.context['request'].user
        return super().create(validated_data)

class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        fields = '__all__'

class DocumentSerializer(serializers.ModelSerializer):
    fields = FieldSerializer(many=True, read_only=True)

    class Meta:
        model = Document
        fields = ['id', 'name', 'description', 'fields', 'created_at', 'updated_at']

class FieldValueSerializer(serializers.ModelSerializer):
    field = FieldSerializer(read_only=True)

    class Meta:
        model = FieldValue
        fields = ['id', 'field', 'business', 'value', 'source', 'source_id', 'created_at', 'updated_at']

class BusinessDocumentSerializer(serializers.ModelSerializer):
    document = DocumentSerializer(read_only=True)
    field_values = serializers.SerializerMethodField()

    class Meta:
        model = BusinessDocument
        fields = ['id', 'business', 'document', 'status', 'field_values', 'created_at', 'updated_at']

    def get_field_values(self, obj):
        # Get field values for this business that correspond to fields in this document
        field_values = FieldValue.objects.filter(
            business=obj.business,
            field__document=obj.document
        )
        return FieldValueSerializer(field_values, many=True).data

class BusinessDetailSerializer(serializers.ModelSerializer):
    documents = BusinessDocumentSerializer(source='businessdocument_set', many=True, read_only=True)

    class Meta:
        model = Business
        fields = ['id', 'name', 'description', 'address', 'phone_number', 'email', 'customer', 'documents', 'created_at', 'updated_at']

class DocumentFieldValuesSerializer(serializers.Serializer):
    document = DocumentSerializer()
    field_values = serializers.SerializerMethodField()
    missing_required_fields = serializers.SerializerMethodField()

    def get_field_values(self, obj):
        document = obj['document']
        business = obj.get('business')
        if not business:
            return []
        
        field_values = FieldValue.objects.filter(
            field__document=document,
            business=business
        )
        return FieldValueSerializer(field_values, many=True).data

    def get_missing_required_fields(self, obj):
        document = obj['document']
        business = obj.get('business')
        if not business:
            return []

        # Get all required fields for this document
        required_fields = document.fields.filter(is_required=True)

        # Get existing field values
        existing_values = FieldValue.objects.filter(
            field__document=document,
            business=business
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
        field_values = FieldValue.objects.filter(
            business=obj.business,
            source='document',
            source_id=obj.id
        )
        return FieldValueSerializer(field_values, many=True).data 